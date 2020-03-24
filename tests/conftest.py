from django.conf import settings

settings.configure(
    INSTALLED_APPS=["tests"],
    DATABASES={
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "db.sqlite3"}
    },
)
