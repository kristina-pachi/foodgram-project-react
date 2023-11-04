from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, pagination, mixins
from wkhtmltopdf.views import PDFTemplateResponse

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
from .filters import RecipeFilter

from recipes.models import (
    User,
    Recipe,
    Ingredient,
    Tag,
    IngredientRecipe,
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('name',)
    pagination_class = None


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
        recipes = get_object_or_404(Recipe, shopper__user=self.request.user)
        for recipe in recipes:
            ingredients = get_object_or_404(IngredientRecipe, recipe=recipe)
            for ingredient in ingredients:
                amount = ingredient.amount
                name, measurement_unit = get_object_or_404(
                    Ingredient, id=ingredient.ingredient)
                if name in result:
                    result[name][1] += amount
                else:
                    result[name] = [measurement_unit, amount]

        response = PDFTemplateResponse(
            request=request,
            template='shopping_list.html',
            filename="shopping_list.pdf",
            context={
                'title': 'Список покупок',
                'ingredients': result
            },
            show_content_in_browser=False,
            cmd_options={'margin-top': 50},
        )
        return response


class CreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class FollowViewSet(CreateDestroyViewSet):

    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        return get_object_or_404(User, folslowing__user=self.request.user)

    def perform_create(self, serializer):
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        serializer.save(
            author=author,
            user=self.request.user
        )


class FavoriteViewSet(CreateDestroyViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        return get_object_or_404(Recipe, follower__user=self.request.user)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('id'))
        serializer.save(
            recipe=recipe,
            user=self.request.user
        )

    def perform_destroy(self, instance):
        print('это он')
        return super().perform_destroy(instance)


class ShoppingListView(CreateDestroyViewSet):

    serializer_class = ShoppingListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        return get_object_or_404(Recipe, shopper__user=self.request.user)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('id'))
        serializer.save(
            recipe=recipe,
            user=self.request.user
        )
