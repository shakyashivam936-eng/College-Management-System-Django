from django.contrib import admin

from .models import IssueReport


@admin.register(IssueReport)
class IssueReportAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_by", "status", "created_at")
    list_filter = ("category", "status", "created_at")
    search_fields = ("title", "description", "created_by__username")
    readonly_fields = ("created_by", "created_at", "updated_at")
