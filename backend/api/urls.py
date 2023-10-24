from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()

router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)
router.register(
    r'users/(?P<id>\d+)/subscribe',
    views.FollowViewSet,
    basename='follow'
)
router.register(
    r'recipes/(?P<id>\d+)/favorite',
    views.FavoriteViewSet,
    basename='favorite'
)
router.register(
    r'recipes/(?P<id>\d+)/shopping_card',
    views.ShoppingListView,
    basename='shopping_card'
)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/', include('djoser.urls')),
]
