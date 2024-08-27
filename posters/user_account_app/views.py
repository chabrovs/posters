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
# Create your views here.


@login_required
def view_user_account(request):
    template_name = 'user_account_app/user_account_view.html'
    user = get_object_or_404(User, id=request.user.id)
    user_fields = [
        (field.name, getattr(user, field.name)) for field in user._meta.fields]
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
            form.save()
            return redirect('user_account_app:view_user_account')
    else:
        form = CustomUserCreatingForm()

    return render(request, 'user_account_app/user_sign_up.html', {'form': form})
