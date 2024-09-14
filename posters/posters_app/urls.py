from django.urls import path
from . import views
# from .views import HomePageView, PosterView, get_image_by_image_id, get_image_by_image_path, reverse_test

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('categories/', views.PosterCategoriesView.as_view(), name='categories'),
    path('all/<str:category_name>', views.CategoryView.as_view(), name='list_posters_in_category'),
    path('create_poster/', views.create_poster, name='create_poster'),
    path('poster/<int:poster_id>/edit', views.edit_poster, name='edit_poster'),
    path('poster/<int:poster_id>/delete', views.delete_poster_by_id, name='delete_poster_by_id'),
    path('user_posters/<int:user_id>', views.create_poster, name='user_posters'),
    path('poster/<int:poster_id>', views.PosterView.as_view(), name='poster_view'),
    path('get_poster_image/<slug:image_id>', views.get_image_by_image_id, name='get_image_by_image_id'),
    # path('get_poster_image/', views.get_image_by_image_id, {'image_id': None}, name='get_default_image'),
    path('get_poster_image/<path:image_path>', views.get_image_by_image_path, name='get_image_by_image_path')
]
