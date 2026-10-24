from django import forms

from .models import FeeStructure, StudentFee, Payment


class FeeStructureForm(forms.ModelForm):

    class Meta:
        model = FeeStructure

        fields = [
            "course",
            "semester",
            "academic_year",
            "tuition_fee",
            "exam_fee",
            "library_fee",
            "hostel_fee",
            "other_fee",
            "is_active",
        ]

        widgets = {
            "academic_year": forms.TextInput(
                attrs={
                    "placeholder": "2026-27"
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        course = cleaned_data.get("course")
        semester = cleaned_data.get("semester")

        if course and semester:

            if semester.course_id != course.id:
                raise forms.ValidationError(
                    "Selected semester does not belong to selected course."
                )

        return cleaned_data


class StudentFeeForm(forms.ModelForm):

    class Meta:
        model = StudentFee

        fields = [
            "student",
            "fee_structure",
            "due_date",
        ]

        widgets = {
            "due_date": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),
        }

    def save(self, commit=True):

        instance = super().save(commit=False)

        # Fee structure ka total fee snapshot karenge
        instance.total_amount = (
            instance.fee_structure.total_fee
        )

        if commit:
            instance.save()

        return instance

class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment

        fields = [
            "amount",
            "payment_mode",
            "transaction_id",
            "remarks",
        ]

        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "1",
                }
            ),
            "transaction_id": forms.TextInput(
                attrs={
                    "placeholder": "UPI/Bank Transaction ID"
                }
            ),
            "remarks": forms.Textarea(
                attrs={
                    "rows": 3
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        fee_structure = cleaned_data.get("fee_structure")

        if student and fee_structure:
            if student.course_id != fee_structure.course_id:
                self.add_error(
                    "fee_structure",
                    "This fee structure is for a different course.",
                )
            elif not fee_structure.is_active:
                self.add_error(
                    "fee_structure",
                    "Choose an active fee structure.",
                )

        return cleaned_data
