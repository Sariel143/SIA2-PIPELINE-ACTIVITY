from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Customer

class AdminRegisterForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise ValidationError("Passwords do not match")
        return password2

    def save(self):
        # Create a superuser using the form data
        user = User.objects.create_superuser(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        return user

class CustomerRegisterForm(UserCreationForm):
    fullname = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Juan Dela Cruz'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Enter a username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'example@gmail.com'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': '09*********'}))
    picture = forms.ImageField(required=False)  # Optional profile picture field
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Choose a strong password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter your password'}))

    class Meta:
        model = User
        fields = ['fullname', 'username', 'email', 'phone', 'picture', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['fullname']
        if commit:
            user.save()
            customer = Customer(
                CustomerName=self.cleaned_data['fullname'],
                Username=self.cleaned_data['username'],
                Email=self.cleaned_data['email'],
                Phone=self.cleaned_data['phone'],
                user=user
            )
            if self.cleaned_data.get('picture'):
                customer.Picture = self.cleaned_data['picture']
            customer.save()
        return user

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        errors = []

        if password1:
            if len(password1) < 8:
                errors.append("This password is too short. It must contain at least 8 characters.")
            if password1 in ['12345678', 'password', '123456']:
                errors.append("This password is too common.")

        if errors:
            raise forms.ValidationError(errors)

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")

        return password2
    
class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise ValidationError("This username does not exist.")
        return username

class PasswordSetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Passwords do not match.")
