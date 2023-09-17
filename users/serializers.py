from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import UserProfile

User = get_user_model()


# registration
class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("email", "name", "password", "password_confirmation")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        password = data.get("password")
        password_confirmation = data.get("password_confirmation")

        if password != password_confirmation:
            raise serializers.ValidationError("Passwords do not match.")

        return data

    def create(self, validated_data):
        validated_data.pop("password_confirmation")
        user = User.objects.create_user(**validated_data)
        return user


# login
class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                email=email,
                password=password,
            )

            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is not active.")

                data["user"] = user
            else:
                raise serializers.ValidationError(
                    "Unable to login with provided credentials."
                )
        else:
            raise serializers.ValidationError(
                'Must include "username_or_email" and "password" fields.'
            )

        return data


# change password
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


# profile
class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    bio = serializers.CharField()

    class Meta:
        model = UserProfile
        fields = ("bio", "name")
