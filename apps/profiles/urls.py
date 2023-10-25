from django.urls import path, include
from apps.profiles.views import ProfileViewSet, MyProfileView, ProfileFollowView
from rest_framework.routers import DefaultRouter

app_name = "profile"

router = DefaultRouter()
router.register("", ProfileViewSet)

urlpatterns=[
    path("me/", MyProfileView.as_view(), name="myprofile"),
    path('follow/<int:account_id>/', ProfileFollowView.as_view(), name='follow-user'),
    path("",include(router.urls)),
]
