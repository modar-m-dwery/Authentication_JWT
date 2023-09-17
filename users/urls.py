from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (ChangePasswordView, CustomTokenObtainPairView,
                    UserLogoutView, UserProfileViewSet, UserRegistrationView)

router = DefaultRouter()
router.register(r"profile", UserProfileViewSet, basename="profile")


urlpatterns = [
    # authentication
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    # profile
    path("", include(router.urls)),
    # rerefresh token
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
