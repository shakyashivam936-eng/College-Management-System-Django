from django import forms

from .models import Admission


class AdmissionForm(forms.ModelForm):

    class Meta:

        model = Admission

        fields = [
            'first_name',
            'last_name',
            'father_name',
            'mother_name',
            'date_of_birth',
            'gender',
            'email',
            'phone',
            'address',
            'city',
            'state',
            'pincode',
            'course',
            'previous_school',
            'high_school_marks',
            'intermediate_marks',
            'passing_year',
            'profile_photo',
            'high_school_marksheet',
            'intermediate_marksheet',
            'identity_proof',
            'transfer_certificate',
        ]

        widgets = {

            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'rows': 4
                }
            ),
        }

    def clean_high_school_marks(self):

        marks = self.cleaned_data.get(
            'high_school_marks'
        )

        if marks is not None:

            if marks < 0 or marks > 100:

                raise forms.ValidationError(
                    'Marks must be between 0 and 100.'
                )

        return marks

    def clean_intermediate_marks(self):

        marks = self.cleaned_data.get(
            'intermediate_marks'
        )

        if marks is not None:

            if marks < 0 or marks > 100:

                raise forms.ValidationError(
                    'Marks must be between 0 and 100.'
                )

        return marks