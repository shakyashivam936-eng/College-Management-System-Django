from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        'student_id',
        'first_name',
        'last_name',
        'course',
        'semester',
        'phone',
        'is_active',
        'admission_date',
    )

    search_fields = (
        'student_id',
        'first_name',
        'last_name',
        'email',
        'phone',
        'father_name',
    )

    list_filter = (
        'course',
        'semester',
        'gender',
        'is_active',
        'admission_date',
    )

    ordering = (
        '-created_at',
    )
