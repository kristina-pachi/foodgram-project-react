from django_filters import rest_framework

from recipes.models import Recipe, Tag


class RecipeFilter(rest_framework.FilterSet):
    """Фильтрация рецептов по тегам и автору."""

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
