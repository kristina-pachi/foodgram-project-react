from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()

router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/subscriptions/', views.APIMyUser.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('users/<int:id>/subscribe/', views.APIFollow.as_view()),
]
