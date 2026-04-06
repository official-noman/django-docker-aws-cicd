"""
Local / development settings.
Usage: DJANGO_SETTINGS_MODULE=app.settings.local
"""

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Allow all origins in local dev
CORS_ALLOW_ALL_ORIGINS = True

# Browsable API in development
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
)

# Disable throttling in dev
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = ()  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}  # noqa: F405

# Shorter token lifetime for easier testing
SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = __import__("datetime").timedelta(minutes=60)  # noqa: F405

# Console-only logging
LOGGING["root"]["handlers"] = ["console"]  # noqa: F405
LOGGING["loggers"]["django"]["handlers"] = ["console"]  # noqa: F405
LOGGING["loggers"]["inventory"]["handlers"] = ["console"]  # noqa: F405
LOGGING["root"]["level"] = "DEBUG"  # noqa: F405
