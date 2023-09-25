import base64

from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField, SlugRelatedField
from django.core.files.base import ContentFile

from recipes.models import (
    User,
    Recipe,
    Ingredient,
    Tag,
    Follow,
    Favorite,
    ShoppingList
)


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')
        read_only_fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'units')
        read_only_fields = '__all__'


class GetRecipeSerializer(serializers.ModelSerializer):
    author = PrimaryKeyRelatedField(queryset=User.objects.all(),)
    image = Base64ImageField(required=False, allow_null=True)
    tag = TagSerializer(many=True)
    ingredient = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'author',
            'image', 'tag', 'description',
            'ingredient', 'cooking_time'
        )


class PostRecipeSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    tag = SlugRelatedField(
        slug_field='slug',
        queryset=Tag.objects.all(),
        many=True
    )
    ingredient = SlugRelatedField(
        slug_field='name',
        queryset=Ingredient.objects.all(),
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'author',
            'image', 'tag', 'description',
            'ingredient', 'cooking_time'
        )


class FollowSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    author = SlugRelatedField(
        required=True,
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = ('user', 'author')


class FavoriteSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    recipe = SlugRelatedField(
        required=True,
        queryset=Recipe.objects.all(),
        slug_field='name',
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingListSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    recipe = SlugRelatedField(
        required=True,
        queryset=Recipe.objects.all(),
        slug_field='name',
    )

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')
