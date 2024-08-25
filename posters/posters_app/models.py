from django.db import models
import uuid
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
#NOTE: MAKE SURE THIS MODULE AND METHODS ARE CORRECTLY IMPORTED BEFORE MIGRATE!\
# (22.08.24) <devbackend_22_08_models>.
from .business_logic.phone_number_logic import standardize_phone_number, validate_phone_number
from .business_logic.poster_image_name_logic import GetUniqueImageName, validate_image_size, DEFAULT_IMAGE
from .business_logic.poster_currency_logic import validate_currency
from .business_logic.posters_lite_logic import get_expire_timestamp
# Create your models here.


#region: SHARED MODELS ###

class PosterCategories(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name
#endregion    

#region: POSTER MODELS ###

class Poster(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_posters')
    status = models.BooleanField(default=True)
    #NOTE: ADD TIMEZONES BEFORE MIGRATE! #UPDATE: ADDED AUTOMATICALLY BY DJANGO (if USE_TZ = True is 'settings.py')\
    # (22.08.24) <devbackend_22_08_models>.
    created = models.DateTimeField(auto_now_add=True)
    deleted = models.DateTimeField(null=True, blank=True)
    #NOTE: ADD VALIDATORS TO THE PHONE_NUMBER FIELD. IN ORDER TO HAVE A CLEAR ERROR\
    # (23.08.24)<devbackend_23_08_migrated>.
    phone_number = models.CharField(max_length=20, validators=[validate_phone_number])
    email = models.EmailField(max_length=255, null=True, blank=True)
    #NOTE: MAKE SURE SESSION IS AVAILABLE BEFORE ANY VIEW REQUEST IT, OTHERWISE IT WILL RAISE SESSION DOES NOT EXIST ERROR.\
    # THIS SETTING IS DONE VIA CUSTOM SESSION MIDDLEWARE! (22.08.24) <devbackend_22_08_models>.
    client = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True, db_column='client', to_field='session_key')
    header = models.CharField(max_length=255)
    description = models.TextField(max_length=10000)
    category = models.ForeignKey('PosterCategories', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=5)
    currency = models.CharField(max_length=3, validators=[validate_currency])

    def __repr__(self) -> str:
        return f"id: ({self.id}) header: ({self.header}) status: ({self.status})"
    
    def __str__(self) -> str:
        return self.header
    
    def save(self, *args, **kwargs):
        self.phone_number = standardize_phone_number(self.phone_number)
        super().save(*args, **kwargs)


class PosterImages(models.Model):
    id = models.AutoField(primary_key=True)
    poster_id = models.ForeignKey('Poster', on_delete=models.CASCADE, related_name='porter_images')
    #NOTE: set default
    image_path = models.ImageField(upload_to=GetUniqueImageName(media_subdirectory='poster_images'), default=DEFAULT_IMAGE, null=True, blank=True, validators=[validate_image_size])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

#endregion 

#region: POSTE LITE MODELS ###

class PosterLite(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    #NOTE: Write an auto cleaner for lite posters where the owner session_key was deleted. (Or change on_delete=models.CASCADE)\
    # (23.08.24) <devbackend_23_08_migrated>.
    owner = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, related_name='owned_posters_lite')
    status = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    #NOTE: FINISH ME. (24.28.24) <devbackend_24_08_views>.
    # expires = models.DateTimeField(default=get_expire_timestamp)
    deleted = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, validators=[validate_phone_number])
    email = models.EmailField(max_length=255, null=True, blank=True)
    client = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True, db_column='client', to_field='session_key')
    header = models.CharField(max_length=255)
    description = models.TextField(max_length=10000)
    category = models.ForeignKey('PosterCategories', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    currency = models.CharField(max_length=3, validators=[validate_currency])

    def __repr__(self) -> str:
        return f"id: ({self.id}) header: ({self.header}) status: ({self.status})"

    def __str__(self) -> str:
        return self.header 
    
    def save(self, *args, **kwargs):
        self.phone_number = standardize_phone_number(self.phone_number)
        super().save(*args, **kwargs)


class PosterLiteImages(models.Model):
    id = models.AutoField(primary_key=True)
    poster_id = models.ForeignKey('PosterLite', on_delete=models.CASCADE, related_name='porterLite_images')
    image_path = models.ImageField(upload_to=GetUniqueImageName(media_subdirectory='poster_lite_images'), default=DEFAULT_IMAGE, null=True, blank=True, validators=[validate_image_size])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __repr__(self) -> str:
        return f"Image poster_id={self.poster_id}"

    def __str__(self) -> str:
        return f"Image for poster id: ({self.poster_id})" 

#endregion 