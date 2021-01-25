import os

import django

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = "NOTASECRET"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": True,
    },
}

INSTALLED_APPS = ["tests"]

if django.VERSION >= (3, 2):  # pragma: no cover
    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
