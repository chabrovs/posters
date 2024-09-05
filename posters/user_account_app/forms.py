from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .business_logic.auth_logic import EmailVerification

class CustomUserCreatingForm(UserCreationForm):
    # email = forms.EmailField(required=False, help_text="Not required")
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class EmailLogInForm(forms.Form):
    email = forms.EmailField(max_length=120, widget=forms.EmailInput(attrs={
        "placeholder": "your email"
    }))

    def send_verification_code(self) -> None:
        email_verification = EmailVerification()
        EmailVerification.send_code(email=self.cleaned_data['email'])


class EmailLogInCodeVerificationForm(forms.Form):
    email = forms.EmailField(
        max_length=120,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "your email"
            }))
    code = forms.IntegerField(widget=forms.TextInput(attrs={
        "placeholder": "enter code from your email"
    }))
