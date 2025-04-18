from django.urls import path
from . import views
from .views import recipe_list, recipe_create, recipe_update, recipe_delete, like_recipe, rate_recipe, group_list, group_create, group_detail, join_group, leave_group, view_trip_list, add_to_trip_list

urlpatterns = [
    path('', views.index, name='index'),            #### Frontend Paths
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'), #### Authentication Paths
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('recipe_list/', recipe_list, name='recipe_list'),       ############## Recipe views   # Public recipe list ###############
    path('<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),    # Public recipe details
    path('create/', recipe_create, name='recipe_create'),  # Requires login
    path('<int:recipe_id>/edit/', recipe_update, name='recipe_update'),  
    path('<int:recipe_id>/delete/', recipe_delete, name='recipe_delete'), 
    path('<int:recipe_id>/like/', like_recipe, name='like_recipe'),  
    path('<int:recipe_id>/rate/', rate_recipe, name='rate_recipe'),
    path('groups/', group_list, name='group_list'), #################### Group views ###############
    path('groups/main/', views.group_main, name='group_main'),
    path('groups/create/', group_create, name='group_create'),
    path('groups/<int:group_id>/', group_detail, name='group_detail'),
    path('groups/<int:group_id>/join/', join_group, name='join_group'),
    path('groups/<int:group_id>/leave/', leave_group, name='leave_group'),
    path('trip/list/', view_trip_list, name='trip_list'), ############ Ingredient Trip view ###############
    path('vote/<int:recipe_id>/', views.vote_recipe, name='vote_recipe'),
    path('trip/add/<int:ingredient_id>/', add_to_trip_list, name='add_to_trip'),
    path('chatbot/', views.chatbot_response, name='chatbot_response'), ########## Chatbot view ###############
]