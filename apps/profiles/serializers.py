from rest_framework import serializers
from apps.profiles.models import Profile , Connection

#
class FollowsProfileSerializer(serializers.ModelSerializer):
    """
    フォローとフォロワーのProfileを取得するためのシリアライザー
    """
    class Meta:
        model = Profile
        fields = ['username', 'created_on', 'img']

class ConnectionSerializer(serializers.ModelSerializer):
    """
    # フォロー機能のためのシリアライザー
    """
    follower = FollowsProfileSerializer(source='follower', read_only=True)
    following = FollowsProfileSerializer(source='following', read_only=True)

    class Meta:
        model = Connection
        fields = ['follower', 'following']



# プロフィールモデルにフォローとフォロワーを格納する
class ProfileSerializer(serializers.ModelSerializer):
    """
    # プロフィールモデルにフォローとフォロワーを格納する
    """
    followings = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    created_on = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    updated_on = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'account',  'created_on', 'updated_on', 'img', 'followings', 'followers']
        extra_kwargs = {"account": {"read_only": True}}

    def get_followings(self, profile_instance):
        """
        フォローしているプロフィールを取得する関数
        """
        followings = Connection.objects.filter(follower=profile_instance)
        following_profiles = [connection.following for connection in followings]
        return FollowsProfileSerializer(following_profiles, many=True).data

    def get_followers(self, profile_instance):
        """
        フォローされているプロフィールを取得する関数
        """
        followers = Connection.objects.filter(following=profile_instance)
        follower_profiles = [connection.follower for connection in followers]
        return FollowsProfileSerializer(follower_profiles, many=True).data
