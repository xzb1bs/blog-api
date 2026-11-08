import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count
from apps.blog.models import Category, Comment, Post

User = get_user_model()

Local_ENV_ID = "local"
top_authors_limit = 5
percent = 100

def evironment_callback(request):
    """badge near the site name. env id comes from blog_env_id"""
    if settings.BLOG_ENV_ID == Local_ENV_ID:
        return ["Local", "warning"]
    return ["production", "danger"]

def drafts_badge(request):
    """num of drafts, shown near 'posts' in sidebar"""
    return str(Post.objects.filter(status=Post.Status.DRAFT).count())

def is_superuser(request):
    return request.user.is_superuser

def dashboard_callback(request,context):
    published = Post.objects.filter(status=Post.Status.PUBLISHED).count()
    drafts = Post.objects.filter(status=Post.Status.DRAFT).count()
    total_posts = published + drafts
    cards = [
        {"title": "Users", "value": User.objects.count()},
        {"title": "Published posts", "value": published},
        {"title": "Drafts", "value": drafts},
        {"title": "Comments", "value": Comment.objects.count()},
    ]

    categories = Category.objects.annotate(posts_total=Count("posts")).order_by("-posts_total", "name")
    chart = {
        "labels": [category.name for category in categories],
        "datasets": [{
            "label": "Posts",
            "data": [category.posts_total for category in categories],
            "backgroundColor": "var(--color-primary-600)",
        }]
    }

    top_authors = (
        User.objects.annotate(posts_total=Count("posts"))
        .filter(posts_total__gt=0)
        .order_by("-posts_total", "email")[:top_authors_limit]
    )

    table = {
        "headers": ["Author", "Posts"],
        "rows": [[author.email, author.posts_total] for author in top_authors],
    }

    published_percent = round(published* percent / total_posts)if total_posts else 0

    drafts_percent = percent - published_percent if total_posts else 0

    context.update({
        "cards": cards,
        "category_chart": json.dumps(chart),
        "authors_table": table,
        "published_percent": published_percent,
        "drafts_percent": drafts_percent,
    })
    return context