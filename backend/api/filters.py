from django_filters import rest_framework

from recipes.models import Recipe


class RecipeFilter(rest_framework.FilterSet):
    tags = rest_framework.CharFilter(field_name='tag__slug')
    author = rest_framework.CharFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
