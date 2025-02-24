from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

# Custom User Model
class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)


# Recipe Model
class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=255)
    
    def __str__(self):
        return self.title
# Ingredient Model
class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=255)
    quantity = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.quantity} of {self.name}"