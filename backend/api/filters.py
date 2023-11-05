from django_filters import rest_framework
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag, Ingredient


class RecipeFilter(rest_framework.FilterSet):
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
        )
    author = rest_framework.CharFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author'
        )


class IngredientSearchFilter(SearchFilter):
    name = rest_framework.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']
