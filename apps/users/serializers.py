from rest_framework import serializers, validators
from .models import Users

class UsersSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    fullname = serializers.SerializerMethodField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(
        validators=[
            validators.UniqueValidator(
                queryset=Users.objects.all(),
                message='username_taken',
            )
        ],
        error_messages={
            'blank': 'username_required',
        }
    )

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
            "date_joined",
            "is_staff",
            "is_superuser",
        ]
        extra_kwargs = {
            'email': {
                'error_messages': {
                    'invalid': 'email_invalid'
                }
            },
            'github': {
                'error_messages': {
                    'invalid': 'url_invalid'
                }
            },
            'linkedin': {
                'error_messages': {
                    'invalid': 'url_invalid'
                }
            },
            'instagram': {
                'error_messages': {
                    'invalid': 'url_invalid'
                }
            },
        }

    def validate_email(self, value):
        user = self.instance

        if Users.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("email_taken")

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