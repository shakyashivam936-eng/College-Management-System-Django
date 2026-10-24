from django.contrib import admin

# Register your models here.

from .models import (
    Department,
    Course,
    Semester,
    Faculty,
    Subject
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'code',
        'name',
        'is_active',
        'created_at'
    )

    search_fields = (
        'name',
        'code'
    )

    list_filter = (
        'is_active',
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'code',
        'name',
        'department',
        'duration_years',
        'total_semesters',
        'is_active'
    )

    search_fields = (
        'name',
        'code'
    )

    list_filter = (
        'department',
        'is_active'
    )


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'course',
        'semester_label',
        'is_active'
    )

    search_fields = (
        'course__name',
        'name',
        'semester_number',
    )

    list_filter = (
        'course',
        'is_active'
    )

    @admin.display(ordering='semester_number', description='Semester')
    def semester_label(self, obj):
        return obj.display_name


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'employee_id',
        'user',
        'department',
        'designation',
        'is_active'
    )

    search_fields = (
        'employee_id',
        'user__username',
        'user__first_name',
        'user__last_name'
    )

    list_filter = (
        'department',
        'designation',
        'is_active'
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'code',
        'name',
        'semester',
        'faculty',
        'credits',
        'max_marks',
        'is_active'
    )

    search_fields = (
        'code',
        'name'
    )

    list_filter = (
        'semester',
        'faculty',
        'is_active'
    )
