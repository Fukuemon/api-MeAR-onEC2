from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import MyAccountViewSet
from .views import UserViewSet

account_router = DefaultRouter()
account_router.register("", UserViewSet, basename="user")  # basename：URLの末尾につく名前

urlpatterns = [
    path(
        "me/",  # ログインユーザー用のアカウント管理エンドポイント
        MyAccountViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "update",
            }
        ),
        name="me",
    ),
    path(
        "me/change_password/",
        MyAccountViewSet.as_view({"post": "change_password"}),
        name="myaccount-change-password",
    ),  # パスワード変更のエンドポイント
    path("", include(account_router.urls)),  # 管理者用のユーザー管理エンドポイント
]
