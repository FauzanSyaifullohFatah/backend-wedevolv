import os
import random
import time
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
def upload_profile_image(instance, filename):
    ext = filename.split('.')[-1]
    return f"profiles/{instance.username}_{int(time.time())}.{ext}"

def upload_project_image(instance, filename):
    ext = filename.split('.')[-1]
    return  f"projects/{instance.user.username}_{int(time.time())}.{ext}"

def upload_certificate_image(instance, filename):
    ext = filename.split('.')[-1]
    return  f"certificates/{instance.user.username}_{int(time.time())}.{ext}"

class User(AbstractUser):
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

class Project(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    tech = models.TextField(blank=True, null=True, help_text="Pisahkan dengan koma, misal: HTML, CSS, React")
    link_repository = models.URLField(blank=True, null=True)
    link_demo = models.URLField(blank=True, null=True)
    image = models.ImageField(
        upload_to=upload_project_image,
        blank=True,
        null=True
    )
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Certificate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates"
    )
    title = models.CharField(max_length=255)
    issued_by = models.CharField(max_length=255, null=True)
    issue_date = models.DateField(null=True)
    expiration_date = models.DateField(null=True, blank=True)
    id_credential = models.CharField(max_length=255)
    url_credential = models.URLField()
    image = models.ImageField(
        upload_to=upload_certificate_image,
        blank=True,
        null=True
    )
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    skills = models.TextField()