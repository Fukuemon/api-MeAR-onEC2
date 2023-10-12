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

# Create your views here.
