from django.db import models

class Restaurant(models.Model):
    """
    店舗モデル：店舗名、緯度、経度、都道府県、住所
    """
    name = models.CharField(max_length=200)  # 店舗名
    lat = models.CharField(max_length=200)  # 緯度
    lng = models.CharField(max_length=200)  # 経度
    area = models.CharField(max_length=200, null=True, blank=True)  # 都道府県
    address = models.CharField(max_length=200)  # 住所

    def __str__(self):
        return self.name