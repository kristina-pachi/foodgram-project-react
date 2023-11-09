from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import viewsets, permissions, pagination, status
from rest_framework.views import APIView

from .serializers import (
    GetRecipeSerializer,
    PostRecipeSerializer,
    IngredientSerializer,
    TagSerializer,
    FollowSerializer,
    FavoriteSerializer,
    ShoppingListSerializer,
)
from .permissions import IsAuthorPermission
from .filters import RecipeFilter, IngredientSearchFilter

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
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited is not None:
            user = self.request.user
            queryset = Recipe.objects.filter(follower__user=user)
            return queryset
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_in_shopping_cart is not None:
            user = self.request.user
            queryset = Recipe.objects.filter(shopper__user=user)
            return queryset
        queryset = Recipe.objects.all()
        return queryset

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
        print(recipes)
        for id in list(recipes):
            ingredient = IngredientRecipe.objects.filter(id=id)
            print(ingredient)
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


class APIFollow(APIView):

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


class APIFavorite(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        serializer = FavoriteSerializer(data=request.data)
        if serializer.is_valid():
            recipe = get_object_or_404(Recipe, id=id)
            serializer.save(
                recipe=recipe,
                user=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        favorite = get_object_or_404(
            Favorite,
            recipe=recipe,
            user=request.user
        )
        serializer = FavoriteSerializer(favorite)
        favorite.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class APIShoppingList(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        serializer = ShoppingListSerializer(data=request.data)
        if serializer.is_valid():
            recipe = get_object_or_404(Recipe, id=id)
            serializer.save(
                recipe=recipe,
                user=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        shopper = get_object_or_404(
            ShoppingList,
            recipe=recipe,
            user=request.user
        )
        serializer = ShoppingListSerializer(shopper)
        shopper.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
