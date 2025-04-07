from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Recipe, Group, WeeklyVote, Recipe
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, RecipeForm, GroupForm
from datetime import date, timedelta
from django.utils import timezone
from django.http import JsonResponse

################################## Front end applications #############################
def index(request):
    return render(request, "index.html") # Render the index.html template

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")  # Redirect if not logged in
    return render(request, "dashboard.html") # Render the dashboard.html template

#################################### User Authentication #############################
# User Registration View
def register(request):
    if request.method == 'POST': # If the form has been submitted
        form = CustomUserCreationForm(request.POST) # Create a form instance with the submitted data
        if form.is_valid(): # If form is valid
            user = form.save() # Save the user to the database
            login(request, user) # Log the user in
            return redirect('dashboard') # Redirect to dashboard if registration is successful
    else:
        form = CustomUserCreationForm() # Create an instance of the form
    return render(request, 'register.html', {'form': form}) # Render the register.html template

# User Login View
def login_view(request):
    if request.method == 'POST': # If the form has been submitted
        form = CustomAuthenticationForm(request, data=request.POST) # Create a form instance with the submitted data
        if form.is_valid(): # If form is valid
            user = form.get_user() # Get the user
            login(request, user) # Log the user in
            return redirect('dashboard') # Redirect to dashboard if login is successful
    else: 
        form = CustomAuthenticationForm() # Create an instance of the form
    return render(request, 'login.html', {'form': form}) # Render the login.html template

# User Logout View
def logout_view(request):
    logout(request)
    return redirect('index')

################################## User Profile Management #############################
# Profile Management View
@login_required
def profile(request):
    if request.method == 'POST': # If the form has been submitted
        form = UserProfileForm(request.POST, instance=request.user) # Create a form instance with the submitted data
        if form.is_valid(): # If form is valid
            form.save() # Save the form
            return redirect('dashboard') # Redirect to dashboard if profile is updated
    else:
        form = UserProfileForm(instance=request.user) # Create an instance of the form
    return render(request, 'profile.html') # Render the profile.html template

############################ Recipe Management #############################
# Recipe List View
def recipe_list(request): 
    recipes = Recipe.objects.all()  # Fetch all recipes
    return render(request, 'recipe_list.html', {'recipes': recipes})  # Render the recipe list template

# Recipe Detail View
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)  # Fetch the specific recipe
    ingredients = recipe.ingredients.all()  # Get all ingredients related to the recipe

    return render(request, 'recipe_detail.html', {
        'recipe': recipe,
        'ingredients': ingredients,  # Pass ingredients to the template
    })

@login_required # Ensure the user is logged in to create a recipe
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            return redirect('recipe_list')
        else:
            print(form.errors)  # Debugging line
    else:
        form = RecipeForm()
    return render(request, 'recipe_form.html', {'form': form})  # Render the recipe creation form template

@login_required # Ensure the user is logged in to update a recipe
def recipe_update(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recipe_form.html', {'form': form})  # Render the recipe update form template

@login_required # Ensure the user is logged in to delete a recipe
def recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    if request.method == 'POST':
        recipe.delete()
        return redirect('recipe_list')
    return render(request, 'recipe_confirm_delete.html', {'recipe': recipe})  # Render the recipe deletion confirmation template

@login_required # Ensure the user is logged in to like a recipe
def like_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user in recipe.likes.all():
        recipe.likes.remove(request.user)
    else:
        recipe.likes.add(request.user)
    return redirect('recipe_detail', recipe_id=recipe.id)  # Redirect to the recipe detail page after liking/unliking

@login_required # Ensure the user is logged in to rate a recipe
def rate_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'POST': # If the form has been submitted
        rating = float(request.POST.get('rating')) # Get the rating from the form
        recipe.update_rating(rating)
        return redirect('recipe_detail', recipe_id=recipe.id)  # Redirect to the recipe detail page after rating

############################ Group Management #############################
@login_required
def group_list(request): # List all groups
    groups = Group.objects.all() # Fetch all groups
    return render(request, 'groups/group_list.html', {'groups': groups}) # Render the group list template

# Create Group View
@login_required
def group_create(request): # Create a new group
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            group.members.add(request.user)  # Creator joins automatically
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'groups/group_form.html', {'form': form}) # Render the group creation form template

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    return render(request, 'groups/group_detail.html', {'group': group})

@login_required
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.members.add(request.user)
    return redirect('group_detail', group_id=group.id)

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.members.remove(request.user)
    return redirect('group_list')

def group_main(request):
    return render(request, 'group_main.html')

########## Weekly Voting System ##########
def get_current_week_start():
    today = timezone.now().date()
    return today - timedelta(days=today.weekday())  # Start on Monday

def vote_recipe(request, recipe_id):
    if request.user.is_authenticated:
        # Get the start of the current week
        week_start = get_current_week_start()
        if not WeeklyVote.objects.filter(user=request.user, week_start=week_start).exists():
            recipe = get_object_or_404(Recipe, id=recipe_id)
            # Save the vote for this recipe and user
            WeeklyVote.objects.create(user=request.user, recipe=recipe, week_start=week_start)
        return redirect('recipe_detail', recipe_id=recipe_id)
    else:
        return redirect('login')  # Redirect to login page if the user is not authenticated
def weekly_top_recipe(request):
    week_start = get_current_week_start()
    votes = WeeklyVote.objects.filter(week_start=week_start)
    top_recipes = votes.values('recipe').annotate(total=models.Count('id')).order_by('-total')
    top_recipe = Recipe.objects.get(id=top_recipes[0]['recipe']) if top_recipes else None
    return render(request, 'weekly_top.html', {'top_recipe': top_recipe})


############################ Ingredient Trip System #############################
def add_to_trip_list(request, ingredient_id):
    if request.user.is_authenticated:
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        IngredientTrip.objects.get_or_create(user=request.user, ingredient=ingredient)
        return JsonResponse({'status': 'added'})
    return JsonResponse({'status': 'unauthenticated'})

@login_required
def view_trip_list(request):
    items = IngredientTrip.objects.filter(user=request.user)
    return render(request, 'trip_list.html', {'items': items})



###### Chat bot system ######

# Predefined responses
RESPONSE_DICT = {
    "how do I add a recipe": "Go to your dashboard and click on 'Add Recipe'.",
    "what is ingredient trip": "It's a list where you can save ingredients you need to buy.",
    "how do I vote for a dish": "Visit the 'Top Dish' section in the community tab and vote for your favorite!",
    "how do I contact support": "You can reach us through the 'Contact Us' page in the footer.",
    # More to be added
}


def chatbot_response(request):
    user_input = request.GET.get("question", "").lower()  # Get user input and convert to lowercase
    response = RESPONSE_DICT.get(user_input, "Sorry, I didn’t get that. Try rephrasing?")
    return JsonResponse({"response": response})