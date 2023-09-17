from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import IsAdminUser

schema_view = get_schema_view(
    openapi.Info(
        title="wege API",
        default_version="v1",
        description="wege API from wegw",
        terms_of_service="https://www.remostart.com/terms/",
        contact=openapi.Contact(email="contact@remostart.com"),
        license=openapi.License(name="Your License"),
    ),
)
# schema_view.permission_classes = [IsAdminUser]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("users.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]
