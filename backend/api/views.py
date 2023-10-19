from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, pagination, mixins
from django.views.generic.base import View
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
    Follow,
    Favorite,
    ShoppingList,
    IngredientRecipe,
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
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


class FollowViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):

    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        return get_object_or_404(User, following__user=self.request.user)

    def perform_create(self, serializer):
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        serializer.save(
            author=author,
            user=self.request.user
        )


class FavoriteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.LimitOffsetPagination

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('id'))
        serializer.save(
            recipe=recipe,
            user=self.request.user
        )


class ShoppingListView(View):

    def ingredients(self):
        recipes = get_object_or_404(Recipe, shopper__user=self.request.user)
        for recipe in recipes:
            ingredients = get_object_or_404(IngredientRecipe, recipe=recipe)
            for ingredient in ingredients:
                pass

    template = 'shopping_list.html'
    context = {'title': 'Список покупок'}

    def get(self, request):
        response = PDFTemplateResponse(
            request=request,
            template=self.template,
            filename="shopping_list.pdf",
            context=self.context,
            show_content_in_browser=False,
            cmd_options={'margin-top': 50},
        )
        return response

    def post(self, request):
        pass

    def delete(self, request):
        pass
