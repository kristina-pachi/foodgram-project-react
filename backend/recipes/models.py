from django.core.validators import MinValueValidator
from django.db import models

from users.models import MyUser as User


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(unique=True, max_length=200)
    slug = models.SlugField(unique=True)
    color = models.CharField(unique=True, max_length=16)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(max_length=100)
    measurement_unit = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'measurement_unit')
        ordering = ['name']


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField(max_length=200)
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes')
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(5)],
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class TagRecipe(models.Model):
    """Связанная модель рецепта и тега."""

    tag = models.ForeignKey(
        Tag,
        related_name='recipe_tags',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_tags',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.recipe}: {self.tag}'


class IngredientRecipe(models.Model):
    """Связанная модель рецепта и ингредиента."""

    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
    )

    class Meta:
        unique_together = ('recipe', 'ingredients')

    def __str__(self):
        return f'{self.recipe}: {self.ingredients}, {self.amount}'


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        unique_together = ('author', 'user')
        ordering = ['author']


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_follower'
    )

    class Meta:
        unique_together = ('recipe', 'user')
        ordering = ['recipe']


class ShoppingList(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopper'
    )

    class Meta:
        unique_together = ('recipe', 'user')
        ordering = ['recipe']
