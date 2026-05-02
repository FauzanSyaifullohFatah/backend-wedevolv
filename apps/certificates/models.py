import time
from django.conf import settings
from django.db import models

def upload_certificate_image(instance, filename):
    ext = filename.split('.')[-1]
    return  f"certificates/{instance.user.username}_{int(time.time())}.{ext}"

class Certificates(models.Model):
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