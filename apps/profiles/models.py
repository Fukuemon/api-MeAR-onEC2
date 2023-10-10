from django.db import models
# Create your models here.
from django.conf import settings
from apps.accounts.models import TimestampedModel

def upload_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    # 保存先のファイルパスを生成
    # 生成されたファイルパスは 'avatars/{ユーザープロファイルのID}{ニックネーム}.{拡張子}'という形式になる
    return '/'.join(['avatars', str(instance.userProfile.id) + str(instance.nickName) + str(".") + str(ext)])


class Connection(models.Model):
    """
    フォロー/フォロワー機能のための中間テーブル
    メタ情報： unique_togetherでfollowerとfollowingの組み合わせがユニークになるように設定
    """
    follower = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name="following_connection")
    following = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='follower_friendships')
    class Meta:
        unique_together = ('follower', 'following')
    def __str__(self):
        return f"{self.follower} follows {self.following}"


class Profile(models.Model, TimestampedModel):
    """
    プロフィールモデル： ユーザーのプロフィール情報を管理する
    """
    username = models.CharField(max_length=20 ,null=True, blank=True)
    # Userモデルとリレーション
    account = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='profile',
        on_delete=models.CASCADE
    )
    img = models.ImageField(blank=True, null=True, upload_to=upload_avatar_path)  # アバター画像

    # フォロー関連のフィールド
    followings = models.ManyToManyField(
        'Profile', verbose_name='フォロー中のユーザー', through='Connection',
        related_name='+', through_fields=('follower', 'following')
    )
    followers = models.ManyToManyField(
        'Profile', verbose_name='フォローされているユーザー', through='Connection',
        related_name='+', through_fields=('following', 'follower')
    )

    def __str__(self):
        return self.nickName
