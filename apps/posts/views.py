from rest_framework import viewsets

from .serializers import CommentSerializer, CommentCreateSerializer, PostListSerializer, PostCreateSerializer, \
    TagListSerializer, PostDetailSerializer, PostUpdateSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Post, Tag , Comment
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Post
from .filters import PostFilter




class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PostFilter
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return Post.objects.all()

    def get_object(self, pk=None):
        return get_object_or_404(Post, pk=pk)

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            return [AllowAny()]
        return [IsAuthenticated()]


    def create(self, request, *args, **kwargs):

        post_serializer = PostCreateSerializer(data=request.data)
        if post_serializer.is_valid():
            author = request.user.profile
            post_serializer.save(author=author)
            return Response(post_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        post = self.get_object(pk)
        post_serializer = PostDetailSerializer(post)
        return Response(post_serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, **kwargs):
        partial = kwargs.pop('partial', False)
        post = self.get_object(pk)
        post_serializer = PostUpdateSerializer(post, data=request.data, partial=partial)

        if post_serializer.is_valid():
            post_serializer.save()
            return Response(post_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        post = self.get_object(pk)
        post.delete()
        return Response({'message': 'Post deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class TagListAPIView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagListSerializer

    def list(self, request):
        serializer_data = self.get_queryset()
        serializer = self.serializer_class(serializer_data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)




class CommentAPIView(APIView):
    permission_classes = (IsAuthenticated,)


    def get(self, request, post_id=None):
        comments = Comment.objects.filter(post=post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, post_id=None):
        # URLから取得したpost_idと、認証されたユーザーを使用してコメントを作成
        data = request.data
        data['post'] = post_id
        data['author'] = request.user.profile.id  # これはrequest.userがProfileモデルとリンクされていると仮定しています

        comment_serializer = CommentCreateSerializer(data=data)

        # バリデーションを行い、無効な場合は自動的に例外を発生させる
        comment_serializer.is_valid(raise_exception=True)

        # シリアライザを使用してコメントを保存
        comment_serializer.save()

        return Response({'message': 'Post Comment successfully'},status=status.HTTP_201_CREATED)


class PostLikeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_post(self, post_id):
        try:
            return get_object_or_404(Post, pk=post_id)
        except Post.DoesNotExist:
            return None

    def post(self, request, post_id):
        post = self.get_post(post_id)
        if post:
            post.likes.add(request.user.profile)
            return Response({'message': 'Post liked successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Post does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, post_id):
        post = self.get_post(post_id)
        if post:
            post.likes.remove(request.user.profile)
            return Response({'message': 'Post unliked successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Post does not exist'}, status=status.HTTP_404_NOT_FOUND)


