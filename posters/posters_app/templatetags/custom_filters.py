from django import template
from django.urls import reverse

register = template.Library()


# @register.filter
# def build_safe_image_url_by_image_id(image_id: int | None = None):
#     """
#     Allows to build image_url for Models with None images.
#     Handles the error when there is not relation between an object table 
#     (e.g. Poster) and an image table (e.g. PosterImages).
#     Use it instead of this '{% url 'posters_app:get_image_by_image_id' image.id %}' statement!
#     :Param image_id: id of an Image.
#     """
#     if not image_id:
#         # This case is handled by the process_image_logic module.
#         image_id = 10*10**12
#     return reverse('posters_app:get_image_by_image_id', args=[image_id])
