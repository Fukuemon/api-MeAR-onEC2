from django.contrib import admin
from django.urls import path, include

# Login
from apps.accounts.views import LoginView


urlpatterns = [
    path('admin/', admin.site.urls),
    # Login
    path("login/", LoginView.as_view(), name="login"),
    # ViewSets
    path("account/", include("apps.accounts.urls")),
]

