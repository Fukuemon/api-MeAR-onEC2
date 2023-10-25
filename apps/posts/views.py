from rest_framework import viewsets
from .serializers import CommentSerializer, CommentCreateSerializer, PostListSerializer, PostCreateSerializer, \
    TagListSerializer, PostDetailSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Post, Tag , Comment
from rest_framework import generics
from rest_framework.permissions import AllowAny,  IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Post
from .filters import PostFilter

# Create your views here.



class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PostFilter

    def get_queryset(self):
        return Post.objects.all()

    def get_object(self, pk=None):
        return get_object_or_404(Post, pk=pk)


    def create(self, request):
        post_serializer = PostCreateSerializer(data=request.data)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response(post_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        post = self.get_object(pk)
        post_serializer = PostDetailSerializer(post)
        return Response(post_serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, **kwargs):  # **kwargsを追加
        partial = kwargs.pop('partial', False)  # partial引数を取得
        post_serializer = PostDetailSerializer(self.get_object(pk), data=request.data, partial=partial)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response(post_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        post = self.get_object(pk)
        post.delete()
        return Response({'message': 'Post deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

