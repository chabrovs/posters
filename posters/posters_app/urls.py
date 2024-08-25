from django.urls import path
from . import views
# from .views import HomePageView, PosterView, get_image_by_image_id, get_image_by_image_path, reverse_test

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('create_poster/', views.create_poster, name='create_poster'),
    path('user_posters/<int:user_id>', views.create_poster, name='user_posters'),
    path('poster/<int:poster_id>', views.PosterView.as_view(), name='poster_view'),
    path('get_poster_image/<int:image_id>', views.get_image_by_image_id, name='get_image_by_image_id'),
    path('get_poster_image/<path:image_path>', views.get_image_by_image_path, name='get_image_by_image_path')
]
