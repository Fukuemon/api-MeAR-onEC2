from rest_framework.routers import DefaultRouter
from .views import UserViewSet, MyAccountViewSet
from django.urls import path, include

account_router = DefaultRouter()
account_router.register('', UserViewSet, basename='user')  # basename：URLの末尾につく名前

urlpatterns = [
    path('me/', MyAccountViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'update',
    }), name='me'),  # ログインユーザー用のアカウント管理エンドポイント
    path('me/change_password/', MyAccountViewSet.as_view({'post': 'change_password'}),
         name='myaccount-change-password'),  # パスワード変更のエンドポイント
    path('', include(account_router.urls)),  # 管理者用のユーザー管理エンドポイント
]
