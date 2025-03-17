from django.urls import path
from . import views
from .views import recipe_list, recipe_create, recipe_update, recipe_delete, like_recipe, rate_recipe

urlpatterns = [
    path('', views.index, name='index'),            #### Frontend Paths
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'), #### Authentication Paths
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('', recipe_list, name='recipe_list'),      #### Recipe Paths
    path('<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('create/', recipe_create, name='recipe_create'),
    path('<int:recipe_id>/edit/', recipe_update, name='recipe_update'),
    path('<int:recipe_id>/delete/', recipe_delete, name='recipe_delete'),
    path('<int:recipe_id>/like/', like_recipe, name='like_recipe'),
    path('<int:recipe_id>/rate/', rate_recipe, name='rate_recipe'),
]