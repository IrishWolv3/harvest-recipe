from django.contrib.auth.models import AbstractUser, Group, Permission, User
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now

# Custom User Model
class User(AbstractUser):
    bio = models.TextField(blank=True, null=True) # Bio attribute
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Profile picture attribute for uploading images

    groups = models.ManyToManyField(Group, related_name="custom_user_set", blank=True) # Many-to-many relationship with Group model
    user_permissions = models.ManyToManyField(Permission, related_name="custom_permission_set", blank=True) # Many-to-many relationship with Permission model


# User profile model (extends built-in Django User)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One-to-one relationship with User model
    bio = models.TextField(blank=True, null=True)  # Optional bio field
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)  # Profile picture

    def __str__(self):
        return self.user.username  # Display username when querying objects

User = get_user_model()
def default_user():
    first_user = User.objects.first()
    return first_user.id if first_user else None  # Ensure it returns None if no user exists

# Recipe Model
class Recipe(models.Model):
    User = get_user_model()
    title = models.CharField(max_length=255)
    description = models.TextField()
    ingredients = models.TextField()
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    likes = models.ManyToManyField(User, related_name='liked_recipes', blank=True)
    rating = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)

    def update_rating(self, new_rating):
        total_rating = self.rating * self.rating_count + new_rating
        self.rating_count += 1
        self.rating = total_rating / self.rating_count
        self.save() 

    def __str__(self):
        return self.title
# Ingredient Model
class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')

    def __str__(self): # String representation
        return f"{self.quantity} of {self.name}" 