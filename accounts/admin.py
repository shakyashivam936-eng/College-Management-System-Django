from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'phone',
        'is_staff',
        'is_active',
    )

    list_filter = (
        'role',
        'is_staff',
        'is_active',
    )

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'phone',
    )

    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        (
            'College Information',
            {
                'fields': (
                    'role',
                    'phone',
                ),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'College Information',
            {
                'fields': (
                    'email',
                    'role',
                    'phone',
                ),
            },
        ),
    )