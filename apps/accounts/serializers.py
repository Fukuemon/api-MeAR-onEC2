from .models import User
from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.profiles.models import Profile
from django.contrib.auth.hashers import check_password

class UserSerializer(serializers.ModelSerializer):
    """
    ユーザー情報のシリアライザー
    """
    class Meta:
        model = get_user_model()
        # パスワードは書き込み専用とする
        extra_kwargs = {"password":{"write_only": True}}

class UserCreateSerializer(serializers.ModelSerializer):
    """
    ユーザー登録用のシリアライザー
    """
    username = serializers.CharField(source="profile.username", required=True)
    img = serializers.ImageField(source="profile.img", required=False)

    class Meta:
        model = get_user_model()
        fields = ("email","password","username","img")
        extra_kwargs = {"password":{"write_only": True}}

    def create(self, validated_data):
        """
        ユーザー登録時に呼ばれるメソッド
        :param validated_data:
        :return:
        """
        profile_data = validated_data.pop("profile", {})
        user = get_user_model().objects.create_user(
            email = validated_data["email"],
            password = validated_data["password"]
        )
        Profile.objects.create(user=user, **profile_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    パスワード変更用のシリアライザー
    """
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




