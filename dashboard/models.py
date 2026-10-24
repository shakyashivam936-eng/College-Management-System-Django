from django.db import models

from django.conf import settings


class IssueReport(models.Model):
    CATEGORY_CHOICES = (
        ("STUDENTS", "Students"),
        ("FEES", "Fees"),
        ("ATTENDANCE", "Attendance"),
        ("EXAMS", "Exams"),
        ("HOSTEL", "Hostel"),
        ("OTHER", "Other"),
    )

    STATUS_CHOICES = (
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In progress"),
        ("RESOLVED", "Resolved"),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="issue_reports",
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=140)
    description = models.TextField(max_length=5000)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="OPEN",
    )
    admin_note = models.TextField(blank=True, max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_category_display()}: {self.title}"
