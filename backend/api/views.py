from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import (
    viewsets, permissions,
    pagination, status,
    generics
)
from rest_framework.views import APIView

from .serializers import (
    GetRecipeSerializer,
    PostRecipeSerializer,
    IngredientSerializer,
    TagSerializer,
    FollowSerializer,
    FavoriteSerializer,
    ShoppingListSerializer,
    GetFollowSerializer
)
from .permissions import IsAuthorPermission
from .filters import RecipeFilter, IngredientFilter
from recipes.models import (
    User,
    Recipe,
    Ingredient,
    Tag,
    IngredientRecipe,
    Favorite,
    ShoppingList,
    Follow
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Принимает только GET запросы,
    отдаёт список ингредиентов и ингредидиент по id.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Принимает только GET запросы,
    отдаёт список тегов и тег по id.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Принимает все запросы,
    отдаёт список рецептов и рецепт по id,
    создаёт, редактирует, удаляет рецепт,
    отвечает за избранное и список покупок,
    отдаёт пользователю txt файл.
    """

    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_pagination_class(self):
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_in_shopping_cart is not None:
            return pagination.LimitOffsetPagination
        return pagination.PageNumberPagination

    pagination_class = property(fget=get_pagination_class)

    def get_permissions(self):
        if self.request.method in ('PATCH', 'DELETE'):
            return (IsAuthorPermission(),)
        return super().get_permissions()

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method not in ('GET', 'DELETE'):
            serializer_class = PostRecipeSerializer
        return serializer_class

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):

        result = {}
        recipes = Recipe.objects.filter(
            shopper__user=request.user
        ).values_list('recipe_ingredients', flat=True)

        for id in list(recipes):
            ingredient = IngredientRecipe.objects.filter(id=id)
            name = list(ingredient.values_list(
                'ingredients__name',
                flat=True
            ))[0]
            amount = list(ingredient.values_list('amount', flat=True))[0]
            measurement_unit = list(ingredient.values_list(
                'ingredients__measurement_unit', flat=True
            ))[0]
            if name in result:
                result[name][1] += amount
            else:
                result[name] = [measurement_unit, amount]

        my_file = open("shopping_list.txt", "w+")
        my_file.write("Список покупок \n")

        for name, count in result.items():
            my_file.write(f"{name} - {count[1]} {count[0]}\n")
        my_file.close()

        return FileResponse(open("shopping_list.txt", "rb"))

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):

        if request.method == 'POST':
            serializer = FavoriteSerializer(data=request.data)
            if serializer.is_valid():
                recipe = get_object_or_404(Recipe, id=pk)
                serializer.save(
                    recipe=recipe,
                    user=request.user
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        recipe = get_object_or_404(Recipe, id=pk)
        favorite = get_object_or_404(
            Favorite,
            recipe=recipe,
            user=request.user
        )
        serializer = FavoriteSerializer(favorite)
        favorite.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):

        if request.method == 'POST':
            serializer = ShoppingListSerializer(data=request.data)
            if serializer.is_valid():
                recipe = get_object_or_404(Recipe, id=pk)
                serializer.save(
                    recipe=recipe,
                    user=request.user
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        recipe = get_object_or_404(Recipe, id=pk)
        shopper = get_object_or_404(
            ShoppingList,
            recipe=recipe,
            user=request.user
        )
        serializer = ShoppingListSerializer(shopper)
        shopper.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class APIFollow(APIView):
    """
    Принимает только POST и DELETE запросы,
    создаёт и удаляет объект модели подписок.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        serializer = FollowSerializer(
            data=request.data,
            context={
                'request': self.request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        if serializer.is_valid():
            author = get_object_or_404(User, id=id)
            serializer.save(
                author=author,
                user=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        follow = get_object_or_404(
            Follow,
            author=author,
            user=request.user
        )
        serializer = FollowSerializer(
            follow,
            context={
                'request': self.request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        follow.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class APIMyUser(generics.ListCreateAPIView):
    """
    Принимает только GET запрос,
    отдаёт список подписок.
    """

    serializer_class = GetFollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(following__user=user)
        return queryset
