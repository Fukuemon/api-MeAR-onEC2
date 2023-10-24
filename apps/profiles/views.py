from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.views import APIView
from django.http import Http404

from .models import Profile, Connection
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


# 自身のプロフィールを返すListView
class MyProfileListView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    def get_queryset(self):
        return self.queryset.filter(account=self.request.user)


class ProfileFollowView(APIView):
    """
    フォロー機能のエンドポイント
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def post(self, request, account_id):
        user = request.user
        try:
            target_user_profile = get_object_or_404(Profile, account__id=account_id)
        except Http404:
            return Response({"detail": "対象のユーザーが存在しません"}, status=status.HTTP_404_NOT_FOUND)

        if user.profile == target_user_profile:
            return Response({"detail": "自身をフォローすることはできません"}, status=status.HTTP_400_BAD_REQUEST)
        Connection.objects.create(follower=user.profile, following=target_user_profile)
        return Response({"detail": "フォローに成功しました"}, status=status.HTTP_201_CREATED)

    def delete(self, request, account_id):
        user = request.user
        try: # ユーザーが存在しない場合は404を返す
            target_user_profile = get_object_or_404(Profile, account__id=account_id)
        except Http404:
            return Response({"detail": "対象のユーザーが存在しません"}, status=status.HTTP_404_NOT_FOUND)

        try:
            connection = Connection.objects.get(follower=user.profile, following=target_user_profile)
            connection.delete()
            return Response({"detail": "フォロー解除に成功しました"}, status=status.HTTP_200_OK)
        except Connection.DoesNotExist:
            return Response({"detail": "フォローしていないユーザーです"}, status=status.HTTP_404_NOT_FOUND)