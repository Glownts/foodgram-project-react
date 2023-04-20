"""
Root URL"s configuration for backend project.

Admin zone located on /admin/.

/api/ for interaction with recipe app through API.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]
