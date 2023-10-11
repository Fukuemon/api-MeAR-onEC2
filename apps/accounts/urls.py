from rest_framework.routers import DefaultRouter
from .views import UserViewSet


router = DefaultRouter()
router.register('', UserViewSet, basename='user')  # basename：URLの末尾につく名前
urlpatterns = router.urls