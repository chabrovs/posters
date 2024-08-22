from django.db import models
import uuid
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
#NOTE: MAKE SURE THIS MODULE AND METHODS ARE CORRECTLY IMPORTED BEFORE MIGRATE!\
# (22.08.24) <devbackend_22_08_models>.
from .business_logic.phone_number_logic import standardize_phone_number
from .business_logic.poster_image_name_logic import get_unique_image_name, validate_image
from .business_logic.poster_currency_logic import validate_currency

# Create your models here.

class Poster(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_posters')
    status = models.BooleanField(default=True)
    #NOTE: ADD TIMEZONES BEFORE MIGRATE! #UPDATE: ADDED AUTOMATICALLY BY DJANGO (if USE_TZ = True is 'settings.py')\
    # (22.08.24) <devbackend_22_08_models>.
    created = models.DateTimeField(auto_now_add=True)
    deleted = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=20)
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
        return self.header
    
    def save(self, *args, **kwargs):
        self.phone_number = standardize_phone_number(self.phone_number)
        super().save(*args, **kwargs)


class PosterCategories(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class PosterImages(models.Model):
    id = models.AutoField(primary_key=True)
    poster_id = models.ForeignKey('Poster', on_delete=models.CASCADE, related_name='porter_images')
    image_path = models.ImageField(upload_to=get_unique_image_name, null=True, blank=True, validators=[validate_image])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)