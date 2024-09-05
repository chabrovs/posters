from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from .forms import CustomUserCreatingForm, UserProfileUpdateForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, login
from .forms import EmailLogInForm, EmailLogInCodeVerificationForm
from .business_logic.auth_logic import EmailVerification
# Create your views here.


@login_required
def view_user_account(request):
    template_name = 'user_account_app/user_account_view.html'
    user_fields = [
        (field.name, getattr(request.user, field.name)) for field in request.user._meta.fields]
    context = {
        "user_fields": user_fields
    }
    return render(request, template_name, context)


@login_required
def user_profile_edit(request):
    if request.method == "POST":
        form = UserProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "You profile has been updated successfully!")
            return redirect('user_account_app:view_user_account')
    else:
        form = UserProfileUpdateForm(instance=request.user)

    return render(request, 'user_account_app/user_account_edit.html', {"form": form})


def user_sign_up(request):
    if request.method == 'POST':
        form = CustomUserCreatingForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect('user_account_app:view_user_account')
    else:
        form = CustomUserCreatingForm()

    return render(request, 'user_account_app/user_sign_up.html', {'form': form})


def email_login(request):
    if request.method == "POST":
        form = EmailLogInForm(request.POST)
        if form.is_valid():
            EmailVerification.send_code()
            return redirect("user_account_app:user_email_login_code_verification")
    else:
        form = EmailLogInForm()
    return render(request, 'user_account_app/user_account_email_login.html', {"form": form})

def emaiL_login_verification(request):
    form = EmailLogInCodeVerificationForm()
    return render(request, 'user_account_app/user_account_email_login_verification.html', {"form": form})


@login_required
def deactivate_user(request):
    if request.method == "POST":
        user = request.user
        user.is_active = False
        user.save()
        return redirect("posters_app:home")


@login_required
def delete_user(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        return redirect('posters_app:home')
