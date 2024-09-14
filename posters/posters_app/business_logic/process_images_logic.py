from __future__ import annotations

from django.forms.models import BaseModelFormSet
from .poster_image_name_logic import DEFAULT_IMAGE, DEFAULT_IMAGE_FULL_PATH
from django.shortcuts import get_object_or_404
from django.http.response import FileResponse
from django.db import models
from ..models import PosterImages
from django.core.cache import cache
import io


def get_default_image_response(default_image_full_path: str = DEFAULT_IMAGE_FULL_PATH, content_type: str = 'image/jpeg') -> FileResponse:
    """
    FileResponse with the default image.
    :Param default_image_full_path: The full path to the default image. 
    The default path is stored in the 'posters_image_name_logic` module.
    :Param content_type: the default image content type. Default is 'image/jpeg'.
    """
    return FileResponse(
        io.BytesIO(get_image_data(default_image_full_path)),
        content_type='image/jpeg'
    )


def get_image_data(image_path: str) -> bytes:
    """
    Read image data using a context manager and return image data in bytes..
    :Param image_path: path to the image you want to read. (absolute or relative).
    """
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    return image_data


def get_safe_image_path_by_image_id(model: models.Model, image_id: int | None, default_image_path: str = DEFAULT_IMAGE) -> str:
    """
    Generate image path according to the 'ImageField' in a model.
    If no image path is provided than return the default image.
    :Param model: A Django ORM model that has image_id (as pk.) and image_path (as 'ImageField') fields.
    :Param image_id: A Primary Key of an image in the model. 
    :Param default_image_path: Set default image path. 
    Default is 'DEFAULT_IMAGE' form the module posters_image_name_logic.
    """
    if image_id is None:
        return DEFAULT_IMAGE

    image = get_object_or_404(model, id=image_id)
    return image.image_path.path


def get_safe_image_path_by_image_path(
        model: models.Model,
        image_path: str | None,
        default_image_path: str = DEFAULT_IMAGE) -> str:
    """
    Generate image path according to the 'ImageField' in a model.
    If no image path is provided than return the default image.
    :Param model: A Django ORM model that has image_id (as pk.) and image_path (as 'ImageField') fields.
    :Param image_id: A Primary Key of an image in the model. 
    :Param default_image_path: Set default image path. 
    Default is 'DEFAULT_IMAGE' form the module posters_image_name_logic.
    """

    if not image_path:
        return DEFAULT_IMAGE
    image = get_object_or_404(model, image_path=image_path)
    return image.image_path.path


def get_image_by_image_id_response(image_id: int | None) -> FileResponse:
    try:
        image_path = get_safe_image_path_by_image_id(
            PosterImages, image_id=image_id)

        # Caching
        image_file_cache_key = f'image_by_id={image_path}'
        image_file_data = cache.get(image_file_cache_key)
        if not image_file_data:
            image_file_data = get_image_data(image_path=image_path)
            cache.set(image_file_cache_key, image_file_data, 60*3)

        return FileResponse(io.BytesIO(image_file_data), content_type='image/jpeg')
    except PosterImages.DoesNotExist:
        return get_default_image_response()
    except Exception as e:
        return get_default_image_response()


def get_image_by_image_path_response(image_path: str) -> FileResponse:
    """
    Returns the FileResponse with an image.
    :Param image_path: Image path as it is stored in the 'ImageField' field in a model.
    """
    try:
        return FileResponse(io.BytesIO(get_image_data(get_safe_image_path_by_image_path(PosterImages, image_path))))
    except PosterImages.DoesNotExist:
        return get_default_image_response()
    except Exception as e:
        return get_default_image_response()


def save_image_for_poster(image: models.Model, poster: models.Model) -> None:
    """
    Save image model instance for a specific poster.
    :Param image: Image model instance.
    :Param poster: A Poster model instance.
    """

    image.poster_id = poster
    image.save()


def save_formset_of_images_for_poster(formset: BaseModelFormSet, poster: models.Model) -> None:
    """
    Saves a formset of images models.
    :Param formset: A formset containing Images for a specific poster.
    :Param poster: A Poster model instance.
    """
    images_formset = formset.save(commit=False)
    for image_model_instance in images_formset:
        save_image_for_poster(image_model_instance, poster)


def delete_images_via_formset(formset: BaseModelFormSet) -> None:
    """
    Delete images provided via a formset.
    :Param formset: A formset containing images. This param must contain a queryset
    (a model responsible for Images).
    """

    for image_to_delete in formset.deleted_objects:
        image_to_delete.delete()


def ensure_image_exists(
        instance: models.Model,
        related_field: str,
        image_model: models.Model,
        default_image_path: str = DEFAULT_IMAGE_FULL_PATH) -> None:
    """
    Ensure that the instance has at least one related image. If none exist,
    create a new image with a default image path.

    :Param instance: The model instance (e.g., Poster, Product) that is related to the images.
    :Param related_field: The name of the related field (e.g., 'poster_images' or 'product_images').
    :Param image_model: The model responsible for storing images (e.g., PosterImages, ProductImages).
    :Param default_image_path: The file path to the default image.
    """

    # Get related images
    related_images = getattr(instance, related_field)
    if not related_images.exists():
        fk_field_name = get_fk_field_name(instance, image_model)

        image_instance = image_model(
            image_path=default_image_path
        )

        # Set instance for the image model dynamically.
        setattr(image_instance, fk_field_name, instance)
        image_instance.save()


def get_fk_field_name(instance: models.Models, model: models.Model) -> str:
    """
    Get the Foreign Key field name of a model related to an instance.
    (model(Foreign Key) => instance) (1:1) (1:M).
    :Param instance: A model that is related to the model.
    :Param model: A model that has a Foreign Key related to the instance.
    """
    for field in model._meta.fields:
        if isinstance(field, models.ForeignKey) and field.related_model == instance._meta.model:
            return field.name
    else:
        raise ValueError(
            f"No ForeignKey found in {model.__name__} pointing to {instance.__class__.__name__}")


def process_formset_with_images_for_model(
        formset: BaseModelFormSet, instance: models.Model,
        related_field: str | None = None,
        image_model: str | None = None,
        default_image_path: str | None = DEFAULT_IMAGE_FULL_PATH) -> None:
    """
    Process formset of images for an instance (a model) that has (1:1) or (1:M) relation to an model with images.
    Process workflow: 
        1. save images (new or replaced); 
        2. Handle images deletion; 
        3. Ensure that at least one image presents.
    :Param formset: A formset to be processes. The formset must include the queryset argument.
    :Param instance: A model instance the formset is processed for. (e.g. Poster, Product, etc.).
    :Param related_field: The name of the related field (e.g., 'poster_images' or 'product_images').
    :Param image_model: The model responsible for storing images (e.g., PosterImages, ProductImages).
    :Param default_image_path: The file path to the default image.
    """
    save_formset_of_images_for_poster(formset=formset, poster=instance)
    delete_images_via_formset(formset)
    if related_field and image_model:
        ensure_image_exists(
            instance=instance,
            related_field=related_field,
            image_model=image_model,
            default_image_path=default_image_path
        )
