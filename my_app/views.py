from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Recipe, Group, WeeklyVote, Ingredient, IngredientTrip, Message
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, RecipeForm, GroupForm
from datetime import date, timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.db import models
import spacy

################################## Front end applications #############################
def index(request):
    return render(request, "index.html") # Render the index.html template

@login_required # Ensure the user is logged in to access the dashboard
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
    return redirect('logout.html')

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

@login_required # Ensure the user is logged in to delete their account
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)  # Log them out before deleting
        user.delete()
        return render(request, 'account_deleted.html')  # ✅ Render this
    return redirect('profile')

############################ Recipe Management #############################
# Recipe List View
def recipe_list(request):
    query = request.GET.get('q', '')
    filter_rating = request.GET.get('rating')

    recipes = Recipe.objects.all()

    if query:
        recipes = recipes.filter(title__icontains=query)
    if filter_rating:
        try:
            filter_value = float(filter_rating)
            recipes = recipes.filter(rating__gte=filter_value)
        except ValueError:
            pass

    # Get top voted recipe of the week
    week_start = get_current_week_start()
    votes = WeeklyVote.objects.filter(week_start=week_start)
    top_recipes = votes.values('recipe').annotate(total=models.Count('id')).order_by('-total')
    top_recipe = Recipe.objects.get(id=top_recipes[0]['recipe']) if top_recipes else None

    return render(request, 'recipe_list.html', {
        'recipes': recipes,
        'top_recipe': top_recipe,
        'query': query,
        'filter_rating': filter_rating
    })

# Recipe Detail View
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)  # Fetch the specific recipe
    ingredients = recipe.ingredients.all()  # Get all ingredients related to the recipe

    return render(request, 'recipe_detail.html', {
        'recipe': recipe,
        'ingredients': ingredients,  # Pass ingredients to the template
    })

@login_required
def recipe_create(request): # Ensure the user is logged in to create a recipe
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        instructions = request.POST.get('instructions')
        image = request.FILES.get('image')
        ingredient_names = request.POST.get('ingredients', '').split(',')

        recipe = Recipe.objects.create( # Create a new recipe instance
            title=title,
            description=description,
            instructions=instructions,
            image=image,
            author=request.user
        )

        for name in ingredient_names: # Loop through each ingredient name
            name = name.strip()
            if name:
                ingredient, _ = Ingredient.objects.get_or_create(name=name)
                recipe.ingredients.add(ingredient)

        return redirect('recipe_list') 

    # GET request
    return render(request, 'recipe_form.html')  # Render the recipe creation form template

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
    return render(request, 'recipe_update.html', {'form': form})  # Render the recipe update form template

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
def group_detail(request, group_id): # View group details and messages
    group = get_object_or_404(Group, id=group_id)
    messages = Message.objects.filter(group=group).order_by('timestamp')

    if request.method == 'POST': # If the form has been submitted, get message content
        content = request.POST.get('message') 
        if content:
            Message.objects.create(group=group, user=request.user, content=content)
            return redirect('group_detail', group_id=group.id)

    return render(request, 'groups/group_detail.html', { # Render the group detail template
        'group': group,
        'messages': messages
    })

@login_required # Ensure the user is logged in to join a group
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.members.add(request.user)
    return redirect('group_detail', group_id=group.id)

@login_required # Ensure the user is logged in to leave a group
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.members.remove(request.user)
    return redirect('group_list')

def group_main(request): # Main view for group management
    return render(request, 'group_main.html')

########## Weekly Voting System ##########
def get_current_week_start():
    today = timezone.now().date()
    return today - timedelta(days=today.weekday())  # Start on Monday

def vote_recipe(request, recipe_id): # View to handle voting for a recipe
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
# View to add an ingredient to the trip list
@login_required
def add_to_trip_list(request, ingredient_id):
    if request.user.is_authenticated:
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        IngredientTrip.objects.get_or_create(user=request.user, ingredient=ingredient)
        return JsonResponse({'status': 'added'})
    return JsonResponse({'status': 'unauthenticated'})

# View to display the trip list
@login_required
def view_trip_list(request):
    items = IngredientTrip.objects.filter(user=request.user)
    return render(request, 'trip_list.html', {'items': items})
# View to remove an item from the trip list
@login_required
def delete_from_trip_list(request, item_id):
    item = get_object_or_404(IngredientTrip, id=item_id, user=request.user)
    item.delete()
    return redirect('trip_list')  # or wherever your trip list page is



########## Hybrid Chatbot ##########
# Load spaCy for NLP fallback
nlp = spacy.load("en_core_web_sm")

RESPONSE_DICT = { # Predefined responses for common questions
    "how do i add a recipe": "Go to your dashboard and click on 'Add Recipe'.",
    "what is ingredient trip": "It's a list where you can save ingredients you need to buy.",
    "how do i vote for a dish": "Visit the 'Top Dish' section in the community tab and vote for your favorite!",
    "how do i contact support": "You can reach us through the 'Contact Us' page in the footer.",
    "how do i edit a recipe": "Visit your profile, click the recipe, then select 'Edit'.",
    "how do i delete a recipe": "From the recipe page, click 'Delete' at the bottom.",
    "can i join a group": "Yes! Go to the 'Groups' tab and click 'Join' on any group you like.",
    "how do i leave a group": "Open the group page and click 'Leave Group' at the top.",
    "how do i see my group": "Go to your profile, and you’ll see the group you're part of.",
    "how do i add ingredients to my trip list": "Click the 'Add to Trip List' button beside each ingredient in a recipe.",
    "how do i remove ingredients from my trip list": "Go to your Ingredient Trip List and click the delete button next to the item.",
    "what is top dish of the week": "It's a recipe voted most popular this week by the community.",
    "how do i vote for top dish": "On the recipe page, you’ll find a 'Vote as Top Dish' button.",
    "how do i search for recipes": "Use the search bar at the top of the recipe list page.",
    "how do i reset my password": "Go to login, click 'Forgot Password', and follow the instructions.",
    "how do i change my email": "Visit your profile, then edit your information and save.",
    "can i message other users": "Not yet, but we’re working on a messaging feature!",
    "what file types can i upload for recipe images": "JPG, PNG, and GIF formats are accepted.",
    "why is my recipe not saving": "Make sure all required fields are filled and your image size is under the limit.",
    "how do i report an issue": "Use the 'Contact Us' form or report it in your group discussion.",
    "how are recipes rated": "Other users rate your recipes from 1 to 5 stars.",
    "what are likes": "Likes are quick reactions users can give to recipes they enjoy.",
}

def handle_with_nlp(user_input): # Fallback to NLP for vague questions
    doc = nlp(user_input)
    keywords = ['tomato', 'onion', 'chicken', 'beef', 'rice', 'garlic']  # add more
    if any(word.lower() in user_input for word in keywords):
        return f"Looking for recipes with {user_input}? Try the search bar above!"
    return "Sorry, I didn’t get that. Try rephrasing?"

def chatbot_response(request): # Handle chatbot responses
    user_input = request.GET.get("question", "").lower()
    topic = get_topic_from_question(user_input)

    # Save the topic in session
    if topic:
        request.session["last_topic"] = topic
    else:
        topic = request.session.get("last_topic")

    # Direct match
    response = RESPONSE_DICT.get(user_input)

    # Handle vague questions with context
    if not response and user_input in ["how do i do that", "where is that", "what now", "how does it work"]:
        if topic == "recipe":
            response = "Are you asking about a recipe? You can add, edit, or delete them from your dashboard or profile."
        elif topic == "group":
            response = "For groups, you can join or leave one from the Groups tab."
        elif topic == "trip":
            response = "You can manage your trip list from the Ingredient Trip section in your profile."
        elif topic == "vote":
            response = "You can vote for your favorite recipes directly from their pages."
        elif topic == "profile":
            response = "Profile options like changing email or password are in your profile tab."
        else:
            response = "Could you clarify your question?"
    
    # Fallback to NLP
    if not response:
        response = handle_with_nlp(user_input)

    return JsonResponse({"response": response})

def get_topic_from_question(question): # Determine the topic from the question
    keywords = {
        "recipe": ["recipe", "edit", "delete", "add", "save"],
        "group": ["group", "join", "leave"],
        "trip": ["trip", "ingredient", "list"],
        "vote": ["vote", "top dish"],
        "profile": ["profile", "email", "password"],
    }
    for topic, terms in keywords.items():
        if any(term in question for term in terms):
            return topic
    return None
