from django import forms

from .models import IssueReport


class IssueReportForm(forms.ModelForm):
    class Meta:
        model = IssueReport
        fields = ("category", "title", "description")
        widgets = {
            "category": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "maxlength": 140,
                "placeholder": "Short summary of the issue",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "maxlength": 5000,
                "placeholder": "Describe what happened and any steps to reproduce it.",
            }),
        }


class IssueReportUpdateForm(forms.ModelForm):
    class Meta:
        model = IssueReport
        fields = ("status", "admin_note")
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
            "admin_note": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "maxlength": 2000,
                "placeholder": "Optional response for the person who reported this issue",
            }),
        }
