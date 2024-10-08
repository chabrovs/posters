from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from .models import PosterImages, Poster
from .business_logic.poster_image_name_logic import DEFAULT_IMAGE



#FIXME: Handle case if user deletes all Images from a poster.
# Issue is the poster deleting process breaks.
#NOTE: Unable to delete all posters, when these Signals are enabled ! (devbackend_09_09_tech_loan).

# @receiver(post_delete, sender=PosterImages)
# def ensure_default_image(sender, instance, **kwargs) -> None:
#     poster = instance.poster_id  # Get the related Poster instance

#     # Let a poster to be deleted when it's being deleted.
#     if hasattr(instance, '_deleting'):
#         return

#     if not poster.poster_images.exists():  # Check if there are no remaining images
#         # Create a new PosterImages instance with the default image
#         PosterImages.objects.create(poster_id=poster, image_path=DEFAULT_IMAGE)

# # Pre-delete signal to mark poster as being deleted
# @receiver(pre_delete, sender=Poster)
# def mark_poster_deleting(sender, instance, **kwargs):
#     instance._deleting = True