import time
from django.conf import settings
from django.db import models

def upload_project_image(instance, filename):
    ext = filename.split('.')[-1]
    return  f"projects/{instance.user.username}_{int(time.time())}.{ext}"

class Projects(models.Model):
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

