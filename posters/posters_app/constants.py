from django.conf import settings
import os


RECOMMENDED_POSTERS_CACHE_KEY = 'recommended_posters_cached'
POSTER_VIEW_CACHE_KEY = 'poster_view_query_cached'
CATEGORIES_CACHE_KEY = 'categories_cached'
POSTERS_IN_CAT_QUERY_CACHE_KEY = 'posters_in_category_cached'

DEFAULT_IMAGE = "poster_images/default_image.jpg"
DEFAULT_IMAGE_FULL_PATH = os.path.join(settings.MEDIA_ROOT, DEFAULT_IMAGE)