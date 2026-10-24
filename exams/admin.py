from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import ExamType, Exam, ExamSchedule, StudentMark, ExamResult


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "max_marks",
        "is_active",
        "created_at",
    )

    list_filter = (
        "name",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "exam_type",
        "course",
        "semester",
        "academic_year",
        "start_date",
        "end_date",
        "is_active",
        "result_dashboard",
    )

    list_filter = (
        "exam_type",
        "course",
        "semester",
        "academic_year",
        "is_active",
    )

    search_fields = (
        "name",
        "academic_year",
        "course__name",
        "semester__name",
    )

    autocomplete_fields = (
        "exam_type",
        "course",
        "semester",
    )

    @admin.display(description="Results")
    def result_dashboard(self, obj):
        url = reverse(
            "exams:exam_result_dashboard",
            args=[obj.id],
        )
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">View results</a>',
            url,
        )



@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):

    list_display = (
        "exam",
        "subject",
        "exam_date",
        "start_time",
        "end_time",
        "room",
        "max_marks",
        "pass_marks",
        "marks_entry",
    )

    list_filter = (
        "exam",
        "subject",
        "exam_date",
    )

    search_fields = (
        "exam__name",
        "subject__name",
        "subject__code",
        "room",
    )

    autocomplete_fields = (
        "exam",
        "subject",
    )

    @admin.display(description="Marks")
    def marks_entry(self, obj):
        url = reverse(
            "exams:mark_entry",
            args=[obj.id],
        )
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">Enter marks</a>',
            url,
        )


@admin.register(StudentMark)
class StudentMarkAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "subject",
        "exam_schedule",
        "marks_obtained",
        "attendance",
        "created_at",
    )

    list_filter = (
        "attendance",
        "subject",
        "exam_schedule__exam",
        "exam_schedule__subject",
    )

    search_fields = (
        "student__student_id",
        "student__first_name",
        "student__last_name",
        "subject__name",
        "exam_schedule__subject__name",
    )

    fields = (
        "exam_schedule",
        "student",
        "marks_obtained",
        "attendance",
        "remarks",
    )

    autocomplete_fields = (
        "student",
        "exam_schedule",
    )

    def save_model(self, request, obj, form, change):
        if obj.exam_schedule_id:
            obj.subject = obj.exam_schedule.subject
        super().save_model(request, obj, form, change)


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "exam",
        "total_marks",
        "obtained_marks",
        "percentage",
        "grade",
        "status",
        "published",
    )

    list_filter = (
        "exam",
        "grade",
        "status",
        "published",
    )

    search_fields = (
        "student__student_id",
        "student__first_name",
        "student__last_name",
        "exam__name",
    )

    readonly_fields = (
        "total_marks",
        "obtained_marks",
        "percentage",
        "grade",
        "status",
        "created_at",
        "updated_at",
    )
