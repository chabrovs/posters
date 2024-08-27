from django.urls import path
from . import views


urlpatterns = [
    path("sign_up", views.user_sign_up, name='user_sign_up'),
    path("profile_edit", views.user_profile_edit, name='user_profile_edit'),
    path("view_account", views.view_user_account, name='view_user_account'),
]

#NOTE: Now default URLs for password change, password_reset, etc..