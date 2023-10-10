from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# 継承することで、作成日と更新日を自動で追加するモデル
class TimestampedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)  # 作成日
    updated_on = models.DateTimeField(auto_now=True)  # 更新日

    class Meta:
        abstract = True
        ordering = ['-created_on', '-updated_on']