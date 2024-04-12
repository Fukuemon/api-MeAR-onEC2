from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CommentAPIView
from .views import PostLikeView
from .views import PostViewSet
from .views import TagListAPIView

post_router = DefaultRouter()
post_router.register("", PostViewSet, basename="post")
comment_router = DefaultRouter()


urlpatterns = [
    path("<int:post_id>/like/", PostLikeView.as_view(), name="like"),
    path(
        "<int:post_id>/comment/", CommentAPIView.as_view(), name="comment-list-create"
    ),
    path("tags/", TagListAPIView.as_view(), name="tag"),
    path("", include(post_router.urls), name="post"),
]
