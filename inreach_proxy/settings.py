import os
import sys
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = secrets.token_urlsafe()
DEBUG = True

INSTALLED_APPS = [
    "inreach_proxy",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(asctime)s %(levelname)s %(filename)s %(funcName)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "INFO", "propagate": True, "stream": sys.stdout},
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DATABASE_PATH", BASE_DIR / "db.sqlite3"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
