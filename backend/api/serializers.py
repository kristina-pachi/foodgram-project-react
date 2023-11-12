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
    """Сериалазер для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалазер для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class GetIngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериалазер для GET запросов к связной модели ингредиента и рецепта."""

    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class PostIngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериалазер для POST запросов к связной модели ингредиента и рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(min_value=1,)

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'amount'
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериалазер для пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'id',
            'is_subscribed'
        )
        read_only_fields = ['is_subscribed']

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        following = list(obj.following.values_list('user', flat=True))
        return (
            user.is_authenticated
            and user.id in following
        )


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериалазер для GET запросов рецепта."""

    author = UserSerializer(many=False,)
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
        user = self.context['request'].user
        followers = list(obj.favorite_follower.values_list('user', flat=True))
        return (
            user.is_authenticated
            and user.id in followers
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        shoppers = list(obj.shopper.values_list('user', flat=True))
        return (
            user.is_authenticated
            and user.id in shoppers
        )


class PostRecipeSerializer(serializers.ModelSerializer):
    """Сериалазер для POST и PATCH запросов рецепта."""

    author = SlugRelatedField(slug_field='username', read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )
    ingredients = PostIngredientRecipeSerializer(
        many=True,
        source='recipe_ingredients',
        required=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'author',
            'image', 'tags', 'text',
            'ingredients', 'cooking_time'
        )

    def validate(self, data):
        if not data['name'].isalpha():
            raise serializers.ValidationError(
                'Название может состоять только из букв!')
        return data
    # чтобы ингредиенты были уникальны в рецепте
    # добавила unique_together в связнную модель
    # и также минимальные валидаторы для полей amount, cooking_time

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredients=ingredient['id'],
                amount=ingredient['amount']
            ).save()
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)

        ingredients = validated_data.pop('recipe_ingredients')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredients=ingredient['id'],
                amount=ingredient['amount']
            ).save()

        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.save()
        return instance


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалазер для рецепта без связанных полей."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class GetFollowSerializer(serializers.ModelSerializer):
    """Сериалазер для GET запросов к подпискам."""

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
        return RecipeSerializer(
            obj.recipes,
            many=True,
            context=self.context
        ).data

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        following = list(obj.following.values_list('user', flat=True))
        return (
            user.is_authenticated
            and user.id in following
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериалазер для подписк."""

    class Meta:
        model = Follow
        fields = ('user', 'author')
        read_only_fields = ('user', 'author')

    def validate(self, data):
        author_id = self.context['view'].kwargs['id']
        author = User.objects.filter(id=author_id)
        user = self.context['request'].user
        if author == user:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя!')
        return data

    def to_representation(self, instance):
        return GetFollowSerializer(instance.author, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалазер для избранного."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeSerializer(instance.recipe, context=self.context).data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериалазер для списка покупок."""

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeSerializer(instance.recipe, context=self.context).data
