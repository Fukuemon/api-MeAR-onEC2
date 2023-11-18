from rest_framework import serializers
from .models import Post, Comment, Tag
from apps.restaurants.models import Restaurant

class CommentSerializer(serializers.ModelSerializer):
    """
    コメントのシリアライザー：コメントの取得
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


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    コメントのシリアライザー：コメントの作成
    """
    comment_author = serializers.ReadOnlyField(source='author.username')
    post_author = serializers.ReadOnlyField(source='post.author.username')

    class Meta:
        model = Comment
        fields = "__all__"


class TagListSerializer(serializers.ModelSerializer):
    """
    タグのシリアライザー：タグの取得
    """
    created_on = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    updated_on = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Tag
        fields = '__all__'


class TagNameSerializer(serializers.ModelSerializer):
    """
    タグのシリアライザー：タグの取得
    """

    class Meta:
        model = Tag
        fields = ['tag', 'id']


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'area', 'lat', 'lng', 'url']


class PostListSerializer(serializers.ModelSerializer):
    """
    投稿一覧のシリアライザー
    投稿のid, 投稿者のid, 投稿者, 投稿者画像, レストランの情報, タグ,  カテゴリー, メニュー名, メニュー写真,  いいね, コメント, 訪問日, 作成日時, 更新日時
    """
    author = serializers.ReadOnlyField(source='author.username')
    author_image = serializers.ReadOnlyField(source='author.image.url')
    author_id = serializers.ReadOnlyField(source='author.id')
    likes = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    tags = TagNameSerializer(many=True, read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    created_on = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    updated_on = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    visited_date = serializers.DateField(format="%Y-%m-%d", read_only=True)
    model_exists_flg = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'author_image', 'author_id', 'restaurant', 'tags', 'menu_name', 'menu_photo', 'likes', 'comments', 'visited_date', 'created_on', 'updated_on', 'model_exists_flg']

    def get_likes(self, obj):
        return [{'id': user.id, 'username': user.username} for user in obj.likes.all()]


    def get_model_exists_flg(self, obj):
        return obj.menu_model is not None and bool(obj.menu_model.name)


class PostCreateSerializer(serializers.ModelSerializer):
    restaurant_data = RestaurantSerializer(write_only=True, required=False)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), write_only=True)

    class Meta:
        model = Post
        fields = ['id', 'restaurant', 'tags', 'menu_name', 'menu_photo', 'menu_model', 'review_text', 'score', 'price',
                  'visited_date', 'restaurant_data']
        extra_kwargs = {
            'restaurant': {'required': False},
        }

    def set_tags(self, post, tags_data):
        post.tags.set(tags_data)

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        self.set_tags(post, tags_data)
        return post

    def to_internal_value(self, data):
        validated_data = super().to_internal_value(data)
        restaurant_data = validated_data.pop('restaurant_data', None)

        if restaurant_data:
            missing_fields = [field for field in ['name', 'address', 'area', 'lat', 'lng'] if
                              restaurant_data.get(field) is None]
            if missing_fields:
                error_msg = f"レストランデータに必須のフィールドが不足しています: {', '.join(missing_fields)}"
                raise serializers.ValidationError(error_msg)

            restaurant, created = Restaurant.objects.get_or_create(
                name=restaurant_data['name'],
                defaults={
                    'address': restaurant_data['address'],
                    'area': restaurant_data['area'],
                    'lat': restaurant_data['lat'],
                    'lng': restaurant_data['lng'],
                    'url': restaurant_data.get('url', None),
                }
            )
            validated_data['restaurant'] = restaurant

        return validated_data


class PostDetailSerializer(serializers.ModelSerializer):
    """
    投稿詳細のシリアライザー：投稿者, 投稿日時, レストラン, カテゴリー, メニュー名, メニュー写真, メニューのモデル, レビュー文, タグ, いいね, コメントを表示する
    """
    author = serializers.ReadOnlyField(source='author.username')
    author_image = serializers.ReadOnlyField(source='author.image.url')
    author_id = serializers.ReadOnlyField(source='author.id')
    likes = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    tags = TagNameSerializer(many=True, read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    created_on = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    updated_on = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    visited_date = serializers.DateField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Post
        fields = '__all__'

    def get_likes(self, obj):
        likes_data = []
        for user in obj.likes.all():
            user_data = {
                'id': user.id,
                'username': user.username,
                'avatar_image': user.img.url if user.img else None  # imgが存在しない場合はNoneを返す
            }
            likes_data.append(user_data)
        return likes_data