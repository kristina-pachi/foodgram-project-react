from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser.views import UserViewSet

from . import views
from users.views import MyUserViewSet

app_name = 'api'

router = DefaultRouter()

router.register('users', MyUserViewSet)
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
    path('users/me/', UserViewSet.as_view({'get': 'me'})),
    path('users/set_password/', UserViewSet.as_view({'post': 'set_password'})),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
