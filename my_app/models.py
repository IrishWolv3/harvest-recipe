from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

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

# Recipe Model
class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes') # User attribute
    title = models.CharField(max_length=255) # Title attribute
    
    def __str__(self): # String representation
        return self.title
# Ingredient Model
class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients') # Recipe attribute
    name = models.CharField(max_length=255) # Name attribute
    quantity = models.CharField(max_length=100) # Quantity attribute

    def __str__(self): # String representation
        return f"{self.quantity} of {self.name}" 