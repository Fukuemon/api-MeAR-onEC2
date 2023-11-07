from django.urls import path, include
from apps.profiles.views import ProfileViewSet, MyProfileView, ProfileFollowView, PostByProfileListView, LikedPostsView, \
    LikedPostsByProfileIdView
from rest_framework.routers import DefaultRouter

app_name = "profile"

router = DefaultRouter()
router.register("", ProfileViewSet)

urlpatterns=[
    path("me/", MyProfileView.as_view(), name="myprofile"),
    path('follow/<int:account_id>/', ProfileFollowView.as_view(), name='follow-user'),
    path('<int:profile_id>/posts/', PostByProfileListView.as_view(), name='posts-by-profile'),
    path('posts/liked/', LikedPostsView.as_view(), name='liked-posts'),
    path('<int:profile_id>/posts/liked/', LikedPostsByProfileIdView.as_view(), name='liked-posts-by-user'),
    path("",include(router.urls)),
]
