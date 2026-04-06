"""
WSGI config for app project.
Uses production settings by default (overridden by DJANGO_SETTINGS_MODULE env var).
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.production")

application = get_wsgi_application()
