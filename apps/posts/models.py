from django.db import models

from ..accounts.models import TimestampedModel
from ..profiles.models import Profile
from ..restaurants.models import Restaurant


def upload_post_path(instance, filename):
    ext = filename.split(".")[-1]
    return "/".join(
        [
            "posts",
            str(instance.author.id) + str(instance.menu_name) + str(".") + str(ext),
        ]
    )


def upload_model_path(instance, filename):
    ext = filename.split(".")[-1]
    return "/".join(
        [
            "models",
            str(instance.author.id) + str(instance.menu_name) + str(".") + str(ext),
        ]
    )


SCORE_CHOICES = [
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4"),
    (5, "5"),
]


class Post(TimestampedModel):
    """
    投稿モデル：投稿者、店舗名、タグ、メニュー名、評価、値段、メニュー画像、メニュー3Dモデル、レビュー内容、いいね、訪問日
    """

    author = models.ForeignKey(Profile, related_name="posts", on_delete=models.CASCADE)
    restaurant = models.ForeignKey(
        Restaurant, related_name="posts", on_delete=models.CASCADE
    )
    tags = models.ManyToManyField("Tag", related_name="posts", blank=True)
    menu_name = models.CharField(max_length=200)
    score = models.IntegerField("評価", choices=SCORE_CHOICES, default=3)
    price = models.IntegerField()
    menu_photo = models.ImageField(upload_to=upload_post_path, blank=True, null=True)
    menu_model = models.FileField(upload_to=upload_model_path, blank=True, null=True)
    review_text = models.TextField(blank=True, null=True)
    likes = models.ManyToManyField(
        Profile, related_name="likes", blank=True, verbose_name="Likes"
    )
    visited_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.menu_name


class Tag(TimestampedModel):
    """
    タグモデル：タグ名
    """

    tag = models.CharField(max_length=255)

    def __str__(self):
        return self.tag


class Comment(TimestampedModel):
    """
    コメントモデル：コメント、投稿者、投稿
    """

    comment = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.comment
