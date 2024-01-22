from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..posts.models import Post
from ..posts.serializers import PostListSerializer
from .models import Connection
from .models import Profile
from .serializers import ProfilePatchSerializer
from .serializers import ProfileSerializer


# プロフィールのCRUD操作を行うViewSet
class ProfileViewSet(viewsets.ModelViewSet):
    """
    プロフィールのCRUD操作を行うViewSet
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            return [AllowAny()]
        return [IsAuthenticated()]


# 自身のプロフィールを返すListView


class MyProfileView(APIView):
    serializer_class = ProfileSerializer

    def get(
        self,
        request,
    ):
        profile = Profile.objects.get(account=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request, format=None):
        try:
            profile = Profile.objects.get(account=request.user)
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProfilePatchSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostByProfileListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PostListSerializer

    def get_queryset(self):
        profile_id = self.kwargs["profile_id"]
        # Profile インスタンスの存在を確認
        if not Profile.objects.filter(id=profile_id).exists():
            raise NotFound(detail="Profile not found")
        return Post.objects.filter(author_id=profile_id)


class LikedPostsView(generics.ListAPIView):
    serializer_class = PostListSerializer

    def get_queryset(self):
        # ログインユーザーのプロフィールインスタンスを取得
        profile = self.request.user.profile
        # そのプロフィールに紐づいた「いいね」をされた投稿のみをフィルタリング
        return Post.objects.filter(likes=profile).distinct().order_by("-created_on")


class LikedPostsByProfileIdView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PostListSerializer

    def get_queryset(self):
        profile_id = self.kwargs.get("profile_id")
        return (
            Post.objects.filter(likes__id=profile_id).distinct().order_by("-created_on")
        )


class ProfileFollowView(APIView):
    """
    フォロー機能のエンドポイント
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def post(self, request, profile_id):
        user = request.user
        try:
            target_user_profile = get_object_or_404(Profile, id=profile_id)
        except Http404:
            return Response(
                {"detail": "対象のユーザーが存在しません"}, status=status.HTTP_404_NOT_FOUND
            )

        if user.profile == target_user_profile:
            return Response(
                {"detail": "自身をフォローすることはできません"}, status=status.HTTP_400_BAD_REQUEST
            )
        Connection.objects.create(follower=user.profile, following=target_user_profile)
        return Response({"detail": "フォローに成功しました"}, status=status.HTTP_201_CREATED)

    def delete(self, request, profile_id):
        user = request.user
        try:  # ユーザーが存在しない場合は404を返す
            target_user_profile = get_object_or_404(Profile, id=profile_id)
        except Http404:
            return Response(
                {"detail": "対象のユーザーが存在しません"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            connection = Connection.objects.get(
                follower=user.profile, following=target_user_profile
            )
            connection.delete()
            return Response({"detail": "フォロー解除に成功しました"}, status=status.HTTP_200_OK)
        except Connection.DoesNotExist:
            return Response(
                {"detail": "フォローしていないユーザーです"}, status=status.HTTP_404_NOT_FOUND
            )
