import time
from django.contrib.auth.models import AbstractUser
from django.db import models

def upload_profile_image(instance, filename):
    ext = filename.split('.')[-1]
    return f"profiles/{instance.username}_{int(time.time())}.{ext}"

class Users(AbstractUser):
    role = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    image = models.ImageField(
        upload_to=upload_profile_image,
        blank=True,
        null=True
    )

    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)

    whatsapp = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    country = models.CharField(max_length=100, blank=True)
    is_public_portfolio = models.BooleanField(default=False)

    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(null=True, blank=True)