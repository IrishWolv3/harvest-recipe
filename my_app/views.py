from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
    return render(request, 'index.html')

@login_required
def dashboard(request):
    user_recipes = Recipe.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'recipes': user_recipes})