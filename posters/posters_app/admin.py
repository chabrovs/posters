from django.contrib import admin
from .models import Poster, PosterCategories, PosterImages, PosterLite, PosterLiteImages

# Register your models here.
admin.site.register(Poster)
admin.site.register(PosterCategories)
admin.site.register(PosterImages)
admin.site.register(PosterLite)
admin.site.register(PosterLiteImages)