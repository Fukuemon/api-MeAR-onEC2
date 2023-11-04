# Django adminとauth.adminから必要なモジュールをインポート
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# 多言語化をサポートするgettextをインポート
from django.utils.translation import gettext as _
# このアプリケーションのモデルをインポート
from . import models

class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email']
    # Userの詳細画面でのフィールドのグループ化
    fieldsets = (
        # emailとpasswordのセクション
        (None, {'fields':('email', 'password')}),
        # 個人情報のセクション(フィールド未指定)
        (_('Personal Info'), {'fields': ()}),
        # 権限に関するセクション
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )

admin.site.register(models.User, UserAdmin)