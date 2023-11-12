from django_filters import rest_framework
from rest_framework.filters import SearchFilter
from recipes.models import Recipe, Tag, Ingredient


class RecipeFilter(rest_framework.FilterSet):
    """Фильтрация рецептов по тегам и автору."""

    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = rest_framework.CharFilter(field_name='author__id')
    is_favorited = rest_framework.CharFilter(
        method='filter_favorited',
    )

    def filter_favorited(self, queryset, name, value):
        queryset = queryset.filter(favorite_follower__user=self.request.user)
        return queryset

    is_in_shopping_cart = rest_framework.CharFilter(
        method='filter_shopping_cart',
    )

    def filter_shopping_cart(self, queryset, name, value):
        queryset = queryset.filter(shopper__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author',
            'is_favorited', 'is_in_shopping_cart'
        )


class IngredientSearchFilter(SearchFilter):
    name = rest_framework.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']
