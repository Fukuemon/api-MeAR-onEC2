from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.profiles.views import LikedPostsByProfileIdView
from apps.profiles.views import LikedPostsView
from apps.profiles.views import MyProfileView
from apps.profiles.views import PostByProfileListView
from apps.profiles.views import ProfileFollowView
from apps.profiles.views import ProfileViewSet

app_name = "profile"

router = DefaultRouter()
router.register("", ProfileViewSet)

urlpatterns = [
    path("me/", MyProfileView.as_view(), name="myprofile"),
    path("follow/<int:profile_id>/", ProfileFollowView.as_view(), name="follow-user"),
    path(
        "<int:profile_id>/posts/",
        PostByProfileListView.as_view(),
        name="posts-by-profile",
    ),
    path("posts/liked/", LikedPostsView.as_view(), name="liked-posts"),
    path(
        "<int:profile_id>/posts/liked/",
        LikedPostsByProfileIdView.as_view(),
        name="liked-posts-by-user",
    ),
    path("", include(router.urls)),
]
