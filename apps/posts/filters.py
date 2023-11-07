import django_filters
from django.db.models import Count
from django_filters.rest_framework import FilterSet, OrderingFilter

from .models import Post

class PostFilter(FilterSet):
    tag = django_filters.CharFilter(field_name="tags__tag", lookup_expr="exact")
    author = django_filters.CharFilter(field_name="author__username", lookup_expr="icontains")
    restaurant = django_filters.CharFilter(field_name="restaurant__name", lookup_expr="icontains")
    ordering = OrderingFilter(
        fields=(
            ('likes_count', 'likes_count'),  # likes_countは後でannotateする
            ('created_on', 'created_on'),
            ('updated_on', 'updated_on'),
        )
    )

    class Meta:
        model = Post
        fields = ['tag', 'author', 'restaurant']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # クエリセットにいいねの数のアノテーションを追加する
        self.queryset = self.queryset.annotate(likes_count=Count('likes')).order_by('-likes_count')
