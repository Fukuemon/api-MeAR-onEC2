from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet
from .views import (
PostLikeView,
CommentAPIView,
TagListAPIView,
)


post_router = DefaultRouter()
post_router.register("", PostViewSet, basename='post')
comment_router = DefaultRouter()


urlpatterns = [
    path('<int:post_id>/like/', PostLikeView.as_view(), name='like'),
    path('<int:post_id>/comment/', CommentAPIView.as_view(), name='comment-list-create'),
    path('tags/', TagListAPIView.as_view(), name='tag'),
    path("", include(post_router.urls), name="post"),
]