from django import forms

from .models import Student


class StudentForm(forms.ModelForm):

    class Meta:

        model = Student

        fields = [
            'student_id',
            'user',
            'first_name',
            'last_name',
            'father_name',
            'mother_name',
            'date_of_birth',
            'gender',
            'email',
            'phone',
            'alternate_phone',
            'address',
            'city',
            'state',
            'pincode',
            'course',
            'semester',
            'admission_date',
            'profile_photo',
            'is_active',
        ]

        widgets = {

            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),

            'admission_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'rows': 3
                }
            ),
        }