from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from .models import Customer

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('CustomerID', 'CustomerName', 'user_username', 'user_email', 'Phone')

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Display the fields you want in the list view
    list_display = ['email', 'first_name', 'last_name', 'is_staff']
    # Define which fields to display in the form for creating and updating a user
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Define which fields are required when creating a user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')}
        ),
    )

    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(Customer, CustomerAdmin)