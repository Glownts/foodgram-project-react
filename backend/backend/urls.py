"""
Root URL"s configuration for backend project.

Admin zone located on /admin/.

/redoc/ to see API documentation.

/api/ for interaction with recipe app through API.

/api/users/ for interaction with user app through API.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("recipes.urls")),
    path("api/users/", include("users.urls"))
]
