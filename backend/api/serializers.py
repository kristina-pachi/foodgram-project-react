import base64

from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField, SlugRelatedField
from django.core.files.base import ContentFile

from recipes.models import (
    User,
    Recipe,
    Ingredient,
    Tag,
    Favorite,
    ShoppingList,
    IngredientRecipe,
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


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class GetIngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name'
            'measurement_unit',
            'amount'
        )


class PostIngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),)
    amount = serializers.IntegerField(min_value=1,)

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'amount'
        )


class GetRecipeSerializer(serializers.ModelSerializer):
    author = PrimaryKeyRelatedField(queryset=User.objects.all(),)
    image = Base64ImageField(required=False, allow_null=True)
    tags = TagSerializer(many=True,)
    ingredients = GetIngredientRecipeSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'author',
            'image', 'tags', 'text',
            'ingredients', 'cooking_time',
            'is_in_shopping_cart', 'is_favorited'
        )

    def get_is_favorited(self, obj):
        pass

    def get_is_in_shopping_cart(self, obj):
        pass


class PostRecipeSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = PostIngredientRecipeSerializer(many=True,)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'author',
            'image', 'tags', 'text',
            'ingredients', 'cooking_time'
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        pass


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = User
        fields = (
            'email', 'username',
            'first_name', 'last_name',
            'id', 'is_subscribed',
            'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        recipes = []

        return RecipeSerializer(recipes, many=True, context=self.context).data

    def get_is_subscribed(self, obj):
        pass

    def validate(self, data):
        if data['author'] == data['user']:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя!')
        return data


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
