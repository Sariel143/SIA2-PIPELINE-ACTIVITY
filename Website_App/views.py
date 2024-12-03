from django.shortcuts import render, redirect
from .forms import CustomerRegisterForm
from django.contrib import messages
from .models import Customer
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse
import random
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomerRegisterForm, CustomerLoginForm,  AdminRegisterForm
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
import json
import random
from datetime import datetime
from django.db.models.functions import ExtractMonth, TruncMonth, TruncDate, TruncDay, TruncWeek
from django.contrib.auth.hashers import make_password
from .forms import PasswordResetForm, PasswordSetForm
import logging
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
import os
from django.conf import settings
from decimal import Decimal
from django.utils.timezone import now
from calendar import month_name
from django.db.models import Sum
import requests
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.views.decorators.cache import never_cache
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Q

def register(request):
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('customer_login')
        else:
            # Handle form errors and display them
            error_messages = []
            password_errors = []

            # Collect errors
            for field, errors in form.errors.items():
                # Handle password1 errors
                if field == 'password1':
                    for error in errors:
                        password_errors.append(f"Password: {error}")
                # Handle password2 errors separately
                elif field == 'password2':
                    for error in errors:
                        password_errors.append(f"Password: {error}")
                # Handle other fields normally
                else:
                    error_messages.append(f"{field.capitalize()}: {errors[0]}")

            # Combine all error messages
            if password_errors:
                error_messages.extend(password_errors)

            # Join all error messages with a line break
            if error_messages:
                messages.error(request, '<br>'.join(set(error_messages)))  # Use set to avoid duplicates

            print(form.errors)  # Optional: for debugging
    else:
        form = CustomerRegisterForm()

    return render(request, 'register.html', {'form': form})

def generate_otp():
    """Generate a 6-digit OTP."""
    return random.randint(100000, 999999)

def customer_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                
                # Check if the user is a superuser/admin
                if user.is_superuser:
                    return JsonResponse({"success": True, "redirect_url": reverse('admin_home')})


                # Check if the user is a Customer
                if Customer.objects.filter(user=user).exists():
                    customer = Customer.objects.get(user=user)
                    return handle_customer_login(customer, request)

                # If none of the above, return login failed
                return JsonResponse({"success": False, "message": "Login failed. User not recognized."})

            # Invalid credentials
            return JsonResponse({"success": False, "message": "Invalid username or password."})

    # Render login form if not a POST request
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def handle_customer_login(customer, request):
    """Handle login flow for customers."""
    if request.COOKIES.get(f'verified_{customer.CustomerID}'):
        return JsonResponse({"success": True, "redirect_url": reverse('customer_home')})
    
    otp = generate_otp()
    request.session['otp'] = otp
    request.session['customer_id'] = customer.CustomerID
    send_mail('Your OTP Code', f'Your OTP code is {otp}', settings.DEFAULT_FROM_EMAIL, [customer.user.email])
    
    return JsonResponse({"success": True, "message": "OTP sent to your email", "redirect_url": reverse('otp_verification')})

def otp_verification(request):
    """Verify the OTP for customers, riders, and store owners."""
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        customer_id = request.session.get('customer_id', None)
        rider_id = request.session.get('rider_id', None)
        owner_id = request.session.get('owner_id', None)

        # Verify OTP for customer, rider, or store owner
        if entered_otp == str(stored_otp):
            try:
                if customer_id:
                    customer = Customer.objects.get(CustomerID=customer_id)
                    user = customer.user
                    login(request, user)

                    response = redirect('customer_home')  # Redirect to customer home after OTP verification
                    response.set_cookie(f'verified_{customer.CustomerID}', True, max_age=2*24*60*60)  # 2 days
                    return response
                

            except (Customer.DoesNotExist):
                messages.error(request, "Invalid OTP or user not found.")
        else:
            messages.error(request, "Invalid OTP.")

    return render(request, 'otp_verification.html')

def password_reset_request(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            otp = generate_otp()
            request.session['reset_otp'] = otp  # Store OTP in session
            request.session['reset_username'] = username  # Store username in session

            # Send OTP via email
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            # Return JSON response instead of rendering the template
            return JsonResponse({'success': True, 'email': user.email})

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Username not found. Please check your input.'})

    return render(request, 'password_reset_request.html')

def check_username(request):
    username = request.GET.get('username')
    try:
        user = User.objects.get(username=username)
        return JsonResponse({'exists': True, 'email': user.email})
    except User.DoesNotExist:
        return JsonResponse({'exists': False})

def verify_otp(request):
    user_otp = request.GET.get('otp')
    session_otp = request.session.get('reset_otp')
    
    if str(user_otp) == str(session_otp):
        return JsonResponse({'verified': True})
    else:
        return JsonResponse({'verified': False})

def password_reset_set(request):
    if 'reset_username' not in request.session:
        return redirect('password_reset_request')

    username = request.session.get('reset_username')
    try:
        user = User.objects.get(username=username)

        if request.method == 'POST':
            form = PasswordSetForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data.get('new_password')
                user.password = make_password(new_password)
                user.save()
                messages.success(request, 'Password has been reset successfully!')
                return redirect('customer_login')
        else:
            form = PasswordSetForm()

        return render(request, 'password_reset_set.html', {'form': form})

    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('password_reset_request')
    
def foodhitch(request):
    return render(request, "index.html")


def customer_home(request):
    return render(request, "customer_home.html")

def logout_view(request):


    logout(request)  # Log out the user
    return redirect('index')  # Redirect to your desired page