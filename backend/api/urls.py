from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser.views import UserViewSet

from . import views
from users.views import MyUserViewSet

app_name = 'api'

router = DefaultRouter()

router.register(
    r'users/(?P<id>\d+)/subscribe',
    views.FollowViewSet,
    basename='follow'
)
router.register('users', MyUserViewSet)
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)

urlpatterns = [
    path('users/me/', UserViewSet.as_view({'get': 'me'})),
    path('users/set_password/', UserViewSet.as_view({'post': 'set_password'})),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:id>/favorite/', views.APIFavorite.as_view()),
    path('recipes/<int:id>/shopping_cart/', views.APIShoppingList.as_view()),
    path('', include(router.urls)),
]
