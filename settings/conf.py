from decouple import config

SECRET_KEY = config('BLOG_SECRET_KEY')
DEBUG = config('BLOG_DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('BLOG_ALLOWED_HOSTS', default='localhost').split(',')
ENV_ID = config('BLOG_ENV_ID', default='local')
