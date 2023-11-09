from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from users.views import APIMyUser

app_name = 'api'

router = DefaultRouter()

router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/subscriptions/', APIMyUser.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('recipes/<int:id>/favorite/', views.APIFavorite.as_view()),
    path('recipes/<int:id>/shopping_cart/', views.APIShoppingList.as_view()),
    path('users/<int:id>/subscribe/', views.APIFollow.as_view()),
]
