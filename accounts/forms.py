from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import User


class LoginForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }
        )
    )

    def clean(self):

        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:

            user = authenticate(
                username=username,
                password=password
            )

            if user is None:
                raise forms.ValidationError(
                    'Invalid username or password.'
                )

            if not user.is_active:
                raise forms.ValidationError(
                    'This account is inactive.'
                )

            cleaned_data['user'] = user

        return cleaned_data


class RegistrationForm(UserCreationForm):

    role = forms.ChoiceField(
        choices=tuple(
            choice for choice in User.ROLE_CHOICES
            if choice[0] != 'ADMIN'
        ),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Account role',
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'role',
            'password1',
            'password2',
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'given-name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'family-name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'tel'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'autocomplete': 'new-password'})
