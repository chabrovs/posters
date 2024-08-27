from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class CustomUserCreatingForm(UserCreationForm):
    # email = forms.EmailField(required=False, help_text="Not required")
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')