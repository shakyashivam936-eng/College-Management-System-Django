from django import forms

from students.models import Student
from .models import ExamSchedule, StudentMark


class StudentMarkForm(forms.ModelForm):

    class Meta:
        model = StudentMark

        fields = [
            "student",
            "marks_obtained",
            "attendance",
            "remarks",
        ]

        widgets = {
            "student": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "marks_obtained": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0"
                }
            ),

            "attendance": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        exam_schedule = kwargs.pop(
            "exam_schedule",
            None
        )

        super().__init__(*args, **kwargs)

        if exam_schedule:

            self.fields["student"].queryset = (
                Student.objects.filter(
                    course=exam_schedule.exam.course,
                    semester=exam_schedule.exam.semester,
                    is_active=True
                )
                .order_by("student_id")
            )

            self.fields["marks_obtained"].help_text = (
                f"Maximum marks: {exam_schedule.max_marks}"
            )