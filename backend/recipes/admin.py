from django.contrib import admin

from .models import (
    Recipe,
    Ingredient,
    Tag,
    Follow,
    Favorite,
    TagRecipe,
    IngredientRecipe
)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'followers')
    search_fields = ('name', 'description')
    list_filter = ('author', 'description', 'tag')

    def followers(self, obj):
        from django.db.models import Count
        result = Favorite.objects.filter(recipe=obj)
        return Count(result['recipe__follower'])


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'units')
    search_fields = ('name',)
    list_filter = ('units',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('author',)


@admin.register(Favorite)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('recipe',)


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('tag', 'recipe')


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe')
