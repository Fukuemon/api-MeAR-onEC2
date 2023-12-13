from django.db import models


class Restaurant(models.Model):
    """
    店舗モデル：店舗名、緯度、経度、都道府県、住所, 店舗サイトへのURL
    """

    name = models.CharField(max_length=200)
    lat = models.FloatField(max_length=200)
    lng = models.FloatField(max_length=200)
    area = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200)
    url = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name
