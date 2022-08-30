from django.urls import path, include

from djoser.views import UserViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

app_name='authentify'

urlpatterns = [
    path("register/", UserViewSet.as_view({"post": "create"}), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("verify/", TokenVerifyView.as_view(), name="verify"),
    path(
        "activation/<str:uid>/<str:token>/",
        UserViewSet.as_view({"post": "activation"}),
        name="activation",
    ),
    path(
        "resend-activation/",
        UserViewSet.as_view({"post": "resend_activation"}),
        name="resend_activation",
    ),
    path(
        "password/reset/password/",
        UserViewSet.as_view({"post": "reset_password"}),
        name="reset_password",
    ),
    path(
        "password/reset/password/confirm/<str:uid>/<str:token>/",
        UserViewSet.as_view({"post": "reset_password_confirm"}),
        name="reset_password_confirm",
    ),
]