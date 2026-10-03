from settings.base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "blog_db",
        "USER": "blog_user",
        "PASSWORD": "blog_password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}