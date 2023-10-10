from django.contrib import admin
# Django adminとauth.adminから必要なモジュールをインポート
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# 多言語化をサポートするgettextをインポート
from django.utils.translation import gettext as _
# このアプリケーションのモデルをインポート
from . import models

class ProfileAdmin(admin.ModelAdmin):
    # フォローしている人とフォロワーを表示する
    list_display = ('username', 'get_following_count', 'get_follower_count')

    def get_following_count(self, obj):
        return obj.followings.count()

    def get_follower_count(self, obj):
        return obj.followers.count()

    get_following_count.short_description = 'フォロー中の人数'
    get_follower_count.short_description = 'フォロワーの人数'

# Register your models here.
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.Connection)