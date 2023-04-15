"""
Django settings for backend project.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
#                            Changable settings
# -----------------------------------------------------------------------------

NAME_MAX_LENG = 200
USER_MAX_LENG = 150
TEXT_MAX_LENG = 1000
MEASUREMENT_MAX_LENG = 200
SLUG_MAX_LENG = 200
EMAIL_MAX_LENG = 254
COLOR_MAX_LENG = 7
ROLE_MAX_LENG = 5

COOKING_TIME_MIN = 1
COOKING_TIME_MAX = 300

MIN_AMOUNT_INGREDIENTS = 1
MAX_AMOUNT_INGREDIENTS = 5000

OBJECTS_PER_PAGE = 6

FILE_NAME = "shopping_list.txt"

# -----------------------------------------------------------------------------
#                            .env settings
# -----------------------------------------------------------------------------

dotenv_path = os.path.join(BASE_DIR, "../infra/.env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


def get_list_allowed(allowed: str) -> list:
    return [host.strip() for host in allowed.split(",") if host.strip()]


SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", default=False)
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE",),
        "NAME": os.getenv("DB_NAME",),
        "USER": os.getenv("POSTGRES_USER",),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD",),
        "HOST": os.getenv("DB_HOST",),
        "PORT": os.getenv("DB_PORT",)
    }
}

# -----------------------------------------------------------------------------
#                            Base settings
# -----------------------------------------------------------------------------

ALLOWED_HOSTS = ["*"]

AUTH_USER_MODEL = "users.User"

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

ROOT_URLCONF = "backend.urls"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CSRF_TRUSTED_ORIGINS = ["http://localhost"]

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "recipes.apps.RecipesConfig",
    "users.apps.UsersConfig",
    "api.apps.ApiConfig",

    "django_filters",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        + "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        + "MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        + "CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        + "NumericPasswordValidator",
    },
]

DJOSER = {
    "HIDE_USERS": False,
    "PERMISSIONS": {
        "resipe": ("api.permissions.AuthorAdminOrReadOnly,",),
        "recipe_list": ("api.permissions.AuthorAdminOrReadOnly",),
        "user": ("api.permissions.AuthorAdminOrReadOnly",),
        "user_list": ("api.permissions.AuthorAdminOrReadOnly",),
    },
    "SERIALIZERS": {
        "user": "api.serializers.UserSerializer",
        "user_list": "api.serializers.UserSerializer",
        "current_user": "api.serializers.UserSerializer",
        "user_create": "api.serializers.UserSerializer",
    },
}

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],

    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination."
    + "PageNumberPagination",
    "PAGE_SIZE": OBJECTS_PER_PAGE,
}
