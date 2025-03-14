from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import handler400, handler404, handler500
from app.views import custom_error_404, custom_error_500


handler404 = custom_error_404
handler500 = custom_error_500

urlpatterns = [
    path("", include("app.urls", namespace="app")),
    path("auth/", include("auth_app.urls", namespace="auth")),
    path("captain/", include("user_admin.urls", namespace="admin")),
    path("hub/", include("user.urls", namespace="user")),
    path("auth/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
