from rest_framework import serializers
from .models import Post, Comment, Tag
from apps.restaurants.models import Restaurant

class CommentSerializer(serializers.ModelSerializer):
    """
    コメントのシリアライザー：コメントの取得, 作成
    """
    comment_author = serializers.ReadOnlyField(source='profile.username')
    post_author = serializers.ReadOnlyField(source='post.author.username')
    author_image = serializers.SerializerMethodField()
    created_on = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    def get_author_image(self, obj):
        if obj.author.img and hasattr(obj.author.img, 'url'):
            return obj.author.img.url
        return ''  # またはデフォルトのURL


    class Meta:
        model = Comment
        fields = ('id', 'comment', 'comment_author', 'author_image', 'post_author', 'created_on')