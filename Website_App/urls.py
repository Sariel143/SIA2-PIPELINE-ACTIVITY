from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import register, foodhitch, customer_login, password_reset_request, password_reset_set, check_username,customer_home, logout_view

urlpatterns = [
    path('', foodhitch , name='index'),
    path('register/', register, name='register'),
    path('customer_home/', customer_home, name='customer_home'),
    path('customer_login/', customer_login, name='customer_login'),
    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset/set/', password_reset_set, name='password_reset_set'),
    path('check_username/', check_username, name='check_username'),  # Add this line
    path('logout/', logout_view, name='logout'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)