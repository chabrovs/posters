import uuid
from django.core.exceptions import ValidationError
import os


### [BOCK] EXCEPTIONS ###
class SetUniqueImageNameException(Exception):
    def __init__(self, method: str, exception_arguments: list, message: str = 'Set unique image name exception' ) -> None:
        self.method = method
        self.exception_arguments = exception_arguments
        self.message = message
        super().__init__()

    def __str__(self) -> str:
        return f'\n[Exception MSG]: {self.message}\n[Exception METHOD]: ({self.method})\n[Exception ARGS]: ({self.exception_arguments})'


def get_unique_image_name(instance, image_filename: str | None) -> str:
    """
    Makes a unique filename for user uploaded images.
    (#NOTE: Alter this exception before production. The exception must not the cause the app crush).
    :Param instance: Instance of an Image.
    :Param image_name: The name of an image user uploaded.
    """
    #NOTE: Define the upload path, e.g., 'poster_images/<unique_filename>'
    default_media_subdirectory = 'poster_images'

    if not image_filename or image_filename == '':
        return os.path.join(default_media_subdirectory, '')
    
    splitted_image_name: list = image_filename.split('.')
    image_extension = str(splitted_image_name[-1])
    unique_string = str(uuid.uuid4().hex)
    unique_image_name = unique_string + '.' + image_extension

    return os.path.join(default_media_subdirectory, unique_image_name)


def validate_image(image):
    """
    Make sure that the image is validated.
    :Param: Image.
    """
    #NOTE: check image type.
    file_size = image.file.size
    limit_mb = 5

    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError("Max image size is 5 %s MB" % limit_mb)