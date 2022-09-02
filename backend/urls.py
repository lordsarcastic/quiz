from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("authentify.urls")),
    path("quiz/", include("quiz.urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
