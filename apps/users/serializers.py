from rest_framework import serializers
from .models import Users

class UsersSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Users
        fields = [
            "id",
            "username",
            "email",
            "fullname",
            "first_name",
            "last_name",
            "role",
            "bio",
            "image",
            "github",
            "linkedin",
            "instagram",
            "whatsapp",
            "phone",
            "country",
            "is_public_portfolio",
            "is_verified",

            "is_staff",
            "is_superuser",
        ]

    def validate_username(self, value):
        user = self.instance
        if Users.objects.filter(username=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Username sudah digunakan")
        return value

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_fullname(self, obj):
        return obj.get_full_name() or obj.username

class RegisterSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = [
            "fullname",
            "username",
            "email",
            "password",
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_username(self, value):
        if Users.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username sudah digunakan")
        return value

    def validate_email(self, value):
        if Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def create(self, validated_data):
        fullname = validated_data.pop("fullname")
        password = validated_data.pop("password")

        names = fullname.split(" ", 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ""

        user = Users(
            first_name=first_name,
            last_name=last_name,
            **validated_data
        )

        user.set_password(password)
        user.save()

        return user