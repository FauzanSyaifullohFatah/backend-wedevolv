from rest_framework import serializers
from .models import Certificates

class CertificatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificates
        fields = [
            "id",
            "user",
            "title",
            "issued_by",
            "issue_date",
            "expiration_date",
            "id_credential",
            "url_credential",
            "image",
            "skills",
            "is_visible",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["user", "creates_at", "updated_at"]