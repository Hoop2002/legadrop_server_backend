"""
Django settings for legadrop project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from environ import Env
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = Env(DEBUG=(bool, True))
env.read_env(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", default=True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Application definition

INSTALLED_APPS = [
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_filters",
    "django_celery_beat",
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "rest_framework_simplejwt",
    "corsheaders",
    "social_django",
    "colorfield",
    "core",
    "cases",
    "users",
    "payments",
    "legaemail",
]

CHANNELS_REDIS_HOST = env.str("REDIS_HOST", "localhost")
CHANNELS_REDIS_PORT = env.int("REDIS_PORT", 6379)
CHANNELS_REDIS_DB = env.int("REDIS_DATABASE", 0)

REDIS_CONNECTION_STRING = (
    f"redis://{CHANNELS_REDIS_HOST}:{CHANNELS_REDIS_PORT}/{CHANNELS_REDIS_DB}"
)

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_CONNECTION_STRING],
        },
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

ROOT_URLCONF = "legadrop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/var/tmp/legadrop_cache",
        "TIMEOUT": 60,
        "OPTIONS": {"MAX_ENTRIES": 1000},
    }
}


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend", ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "LegadropApi",
    "DESCRIPTION": "Legadrop project",
    "VERSION": "0.0.1",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",  # shorthand to use the sidecar instead
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "docExpansion": None,
    },
}


WSGI_APPLICATION = "legadrop.wsgi.application"

ASGI_APPLICATION = "legadrop.asgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DATABASE_NAME"),
        "USER": env("DATABASE_USER"),
        "PASSWORD": env("DATABASE_PASSWORD"),
        "HOST": env("DATABASE_HOST"),
        "PORT": env("DATABASE_PORT"),
    }
}

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_TIMEZONE = "Europe/Moscow"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "www/static"
# STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "www/media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

GATEWAYS_SETTINGS = {
    "MOOGOLD_SECRET_KEY": env("MOOGOLD_SECRET_KEY"),
    "MOOGOLD_PARTNER_ID": env("MOOGOLD_PARTNER_ID"),
    "GENSHIN_CATEGORY": env("GENSHIN_CATEGORY"),
    "LAVA_SECRET_KEY": env("LAVA_SECRET_KEY"),
    "LAVA_SHOP_ID": env("LAVA_SHOP_ID"),
}

BASE_URL = env("BASE_URL_APP")
BACK_URL_LAVA = env("BACK_URL_LAVA")


# email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="test@gmail.com")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="key")
EMAIL_PORT = env("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env("EMAIL_USE_SSL", default=False)
SERVER_EMAIL = env("SERVER_EMAIL", default="default")
EMAIL_ADMIN = env("EMAIL_ADMIN", default="default")
# DEFAULT_FROM_EMAIL = 'default from email'


# social auth settings
SOCIAL_AUTH_REQUIRE_POST = True
LOGIN_REDIRECT_URL = "/get_token"
ACTIVATE_JWT = True
AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.vk.VKOAuth2",
    "social_core.backends.telegram.TelegramAuth",
)
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", default="SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"
)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", default="SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"
)

SOCIAL_AUTH_VK_OAUTH2_KEY = env(
    "SOCIAL_AUTH_VK_OAUTH2_KEY", default="SOCIAL_AUTH_VK_OAUTH2_KEY"
)
SOCIAL_AUTH_VK_OAUTH2_SECRET = env(
    "SOCIAL_AUTH_VK_OAUTH2_SECRET", default="SOCIAL_AUTH_VK_OAUTH2_SECRET"
)
VK_APP_ACCESS_TOKEN = env("VK_APP_ACCESS_TOKEN", default="default")


OAUTH2_PROVIDER = {
    "ACCESS_TOKEN_EXPIRE_SECONDS": 3600 * 24 * 30,
}


# cors settings
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS", default=["http://localhost:8000"]
)


# todo fix this shit
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000"]

FREEKASSA_NOTIFY_PREFIX = env(
    "FREEKASSA_NOTIFY_PREFIX", default="f01ebba8-ca68-4256-9ca6-39ed92ae4d78"
)
FREEKASSA_API_KEY = env("FREEKASSA_API_KEY", default="default")
FREEKASSA_SECRET_KEY_ONE = env("FREEKASSA_SECRET_KEY_ONE", default="default")
FREEKASSA_SECRET_KEY_TWO = env("FREEKASSA_SECRET_KEY_TWO", default="default")
FREEKASSA_SHOP_ID = env("FREEKASSA_SHOP_ID", default="default")

TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default="default")
