from django.contrib import admin

from .models import Admission


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):

    list_display = (
        'application_number',
        'first_name',
        'last_name',
        'course',
        'phone',
        'status',
        'submitted_at',
    )

    search_fields = (
        'application_number',
        'first_name',
        'last_name',
        'phone',
        'email',
    )

    list_filter = (
        'status',
        'course',
        'gender',
        'submitted_at',
    )

    readonly_fields = (
        'application_number',
        'submitted_at',
        'reviewed_at',
    )

    ordering = (
        '-submitted_at',
    )
