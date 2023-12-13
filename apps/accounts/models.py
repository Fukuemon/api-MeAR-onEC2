from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


# 継承することで、作成日と更新日を自動で追加するモデル
class TimestampedModel(models.Model):
    """
    作成日時と更新日時を自動で追加する抽象モデル
    メタ情報：
    - このモデルを継承したモデルは、データベースにテーブルを作成しない
    - データベースから取得したオブジェクトを作成日時と更新日時の降順で並び替える
    """

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_on", "-updated_on"]


class UserManager(BaseUserManager):
    """
    ユーザーマネージャーモデル： ユーザーの作成、更新、削除などの操作を行う
    """

    def create_user(self, email, password=None):
        if not email:
            raise ValueError("メールアドレスを設定してください")

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)

        return user

    # スーパーユーザーの作成
    def create_superuser(self, email, password):
        if password is None:
            raise TypeError("Superusers must have a password.")

        user = self.create_user(email, password)
        user.is_staff = True  # admin権限
        user.is_superuser = True  # 全ての権限
        user.save(using=self._db)  # データベースに保存

        return user


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    """
    ユーザーモデル： ユーザーのアカウント情報と権限を管理する
    AbstractBaseUser: ユーザー名、メールアドレス、パスワード、権限などの基本的なフィールドを持つモデル
    PermissionsMixin: ユーザーに権限を付与するためのモデル
    TimestampedModel: 作成日時と更新日時を自動で追加する抽象モデル
    """

    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()  # UserManagerのインスタンスを生成

    USERNAME_FIELD = "email"  # 認証のためのフィールドをデフォルトのusernameからemailに変更

    def __str__(self):
        return self.email

    @property
    def username(self):
        return self.profile.username
