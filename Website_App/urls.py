from django.urls import path
from .views import register,index

urlpatterns = [
    path('', index, name='index'),
    path('register/', register, name='register'),
]
