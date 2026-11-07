from pathlib import Path

from decouple import Config, RepositoryEnv, config as default_config

ENV_FILE = Path(__file__).resolve().parent / ".env"

if ENV_FILE.exists():
    config = Config(RepositoryEnv(str(ENV_FILE)))
else:
    config = default_config

SECRET_KEY = config("BLOG_SECRET_KEY", default="django-insecure-local-key")
DEBUG = config("BLOG_DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("BLOG_ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")
ENV_ID = config("BLOG_ENV_ID", default="local")
