from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    first_name = models.CharField(default='', max_length=64)
    last_name = models.CharField(default='', max_length=128)
    email = models.EmailField(blank=False, unique=True)
    picture_url = models.URLField(default='')
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELDS = ["email"]
