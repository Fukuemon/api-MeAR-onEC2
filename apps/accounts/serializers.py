from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.profiles.models import Profile

from .models import User


class UserSerializer(serializers.ModelSerializer):
    created_on = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    updated_on = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "created_on",
            "updated_on",
            "is_staff",
            "is_superuser",
            "profile",
        )
        # パスワードは書き込み専用とする
        extra_kwargs = {"password": {"write_only": True}}


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="profile.username", required=True)
    img = serializers.ImageField(source="profile.img", required=False)

    class Meta:
        model = get_user_model()
        fields = ("email", "password", "username", "img")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        profile_data = validated_data.pop("profile", {})
        user = get_user_model().objects.create_user(
            email=validated_data["email"], password=validated_data["password"]
        )
        Profile.objects.create(account=user, **profile_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    password1 = serializers.CharField(required=True, write_only=True, min_length=5)
    password2 = serializers.CharField(required=True, write_only=True, min_length=5)

    def validate(self, data):
        # 現在のパスワードが正しいか確認
        if not check_password(data["current_password"], self.context["user"].password):
            raise serializers.ValidationError({"current_password": "現在のパスワードが正しくありません"})

        # 新しいパスワードが一致するか確認
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError({"password2": "パスワードが一致しません"})

        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    pass
