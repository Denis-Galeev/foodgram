from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import TagViewSet, IngredientViewSet, RecipeViewSet
from api.views import UserViewSet, redirect_to_recipe

# from recipes.views import TagViewSet, IngredientViewSet, RecipeViewSet
# from users.views import UserViewSet
# from shortlinks.views import redirect_to_recipe

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router_v1.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('s/<str:code>/', redirect_to_recipe, name='redirect-to-recipe'),
]
