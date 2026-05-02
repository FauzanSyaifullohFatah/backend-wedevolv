from rest_framework import serializers
from .models import Projects

class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = [
            "id",
            "user",
            "title",
            "description",
            "tech",
            "link_repository",
            "link_demo",
            "image",
            "is_visible",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["user", "created_at", "updated_at"]