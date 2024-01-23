import logging

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import FormParser
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..pagination import PaginationClass
from .filters import PostFilter
from .models import Comment
from .models import Post
from .models import Tag
from .serializers import CommentCreateSerializer
from .serializers import CommentSerializer
from .serializers import PostCreateSerializer
from .serializers import PostDetailSerializer
from .serializers import PostListSerializer
from .serializers import PostUpdateSerializer
from .serializers import TagListSerializer

# Loggerの設定
logger = logging.getLogger(__name__)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterer_class = PostFilter
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = PaginationClass

    def get_queryset(self):
        queryset = Post.objects.all()
        return queryset

    def get_object(self, pk=None):
        post = get_object_or_404(Post, pk=pk)
        return post

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        投稿作成
        tagsは整数型にrequestをintに変換してからそのまま保存する
        """
        tags = request.data.getlist("tags[]")  # 'tags[]' のデータを取得
        tags = [int(tag) for tag in tags]  # 文字列を整数に変換
        print(tags)

        post_serializer = PostCreateSerializer(data=request.data)
        if post_serializer.is_valid():
            author = request.user.profile
            post_serializer.save(author=author)

            # tagの処理
            for tag in tags:
                post_serializer.instance.tags.add(tag)
            return Response(post_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        post = self.get_object(pk)

        post_serializer = PostDetailSerializer(post)
        return Response(post_serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, **kwargs):
        partial = kwargs.pop("partial", False)
        post = self.get_object(pk)
        tags = request.data.getlist("tags[]")  # 'tags[]' のデータを取得
        tags = [int(tag) for tag in tags]  # 文字列を整数に変換
        post_serializer = PostUpdateSerializer(post, data=request.data, partial=partial)

        if post_serializer.is_valid():
            post_serializer.save()

            if tags:
                post_serializer.instance.tags.clear()  # 既存のタグを削除
                for tag in tags:
                    post_serializer.instance.tags.add(tag)

            return Response(post_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        post = self.get_object(pk)
        post.delete()
        return Response(
            {"message": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class TagListAPIView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
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
        data["post"] = post_id
        data[
            "author"
        ] = request.user.profile.id  # これはrequest.userがProfileモデルとリンクされていると仮定しています

        comment_serializer = CommentCreateSerializer(data=data)

        # バリデーションを行い、無効な場合は自動的に例外を発生させる
        comment_serializer.is_valid(raise_exception=True)

        # シリアライザを使用してコメントを保存
        comment_serializer.save()

        return Response(
            {"message": "Post Comment successfully"}, status=status.HTTP_201_CREATED
        )


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
            return Response(
                {"message": "Post liked successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, post_id):
        post = self.get_post(post_id)
        if post:
            post.likes.remove(request.user.profile)
            return Response(
                {"message": "Post unliked successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
