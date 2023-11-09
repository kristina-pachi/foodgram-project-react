from django.contrib import admin

from .models import (
    Recipe,
    Ingredient,
    Tag,
    Follow,
    Favorite,
    TagRecipe,
    IngredientRecipe,
    ShoppingList
)


class TagRecipeAdminInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


class IngredientRecipeAdminInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'followers')
    search_fields = ('name', 'text')
    list_filter = ('author', 'text', 'tags')
    inlines = (IngredientRecipeAdminInline, TagRecipeAdminInline)

    def followers(self, obj):
        result = Favorite.objects.filter(recipe=obj)
        return len(list(result))


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    inlines = (IngredientRecipeAdminInline,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    inlines = (TagRecipeAdminInline,)


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


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('recipe',)
