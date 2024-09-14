import uuid
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
import os
from django.conf import settings


DEFAULT_IMAGE = "poster_images/default_image.jpg"
DEFAULT_IMAGE_FULL_PATH = os.path.join(settings.MEDIA_ROOT, DEFAULT_IMAGE)


#region: EXCEPTIONS
class SetUniqueImageNameException(Exception):
    def __init__(self, method: str, exception_arguments: list, message: str = 'Set unique image name exception' ) -> None:
        self.method = method
        self.exception_arguments = exception_arguments
        self.message = message
        super().__init__()

    def __str__(self) -> str:
        return f'\n[Exception MSG]: {self.message}\n[Exception METHOD]: ({self.method})\n[Exception ARGS]: ({self.exception_arguments})'

#endregion

#region: BUSINESS LOGIC

@deconstructible
class GetUniqueImageName:
    def __init__(self, media_subdirectory: str = 'unknown_images') -> None:
        self.model_instance = media_subdirectory

    def __call__(self, instance, image_filename: str | None) -> str:
        """
        Makes a unique filename for user uploaded images.
        :Param instance: Instance of an Image.
        :Param image_name: The name of an image user uploaded.
        """
        #NOTE: Define the upload path, e.g., 'poster_images/<unique_filename>'

        if not image_filename or image_filename == '':
            return os.path.join(self.model_instance, '')
        
        splitted_image_name: list = image_filename.split('.')
        image_extension = str(splitted_image_name[-1])
        unique_string = str(uuid.uuid4().hex)
        unique_image_name = unique_string + '.' + image_extension

        return os.path.join(self.model_instance, unique_image_name)

#endregion

#region: VALIDATORS

def validate_image_size(image):
    """
    Make sure that the image is validated.
    :Param: Image.
    """
    #NOTE: check image type.
    file_size = image.file.size
    limit_mb = 5

    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError("Max image size is 5 %s MB" % limit_mb)

#endregion