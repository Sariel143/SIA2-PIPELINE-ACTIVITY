from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.utils import timezone
import random
import string
import requests
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.
class Customer(models.Model):
    CustomerID = models.BigAutoField(primary_key=True)
    CustomerName = models.CharField(max_length=100)
    Username = models.CharField(max_length=100, unique=True, default='default_username')
    Email = models.EmailField(default='example@example.com')
    Phone = models.CharField(max_length=15, null=True, blank=True)
    Picture = models.ImageField(upload_to='profile_pictures', null=True, blank=True)
    Password = models.CharField(max_length=128, default='')
    Points = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Hash password only when the customer instance is created
        if self.pk is None and self.Password:
            self.Password = make_password(self.Password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.CustomerName
    
class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    # Set related_name to avoid clash with auth.User's related_name
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Custom related name to prevent clash
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Custom related name to prevent clash
        blank=True,
        help_text='Specific permissions for this user.'
    )

    USERNAME_FIELD = 'email'  # Use email as the unique identifier
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']  # These fields are required on user creation
    
    def __str__(self):
        return self.email