from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.blog.views import UserRegistrationView

urlpatterns = [
    path("", RedirectView.as_view(url="/api/", permanent=False), name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("apps.blog.urls")),
    path("api/auth/register/", UserRegistrationView.as_view(), name="user_register"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]