from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.blog.views import (
    CategoryViewSet,
    PostCommentListCreateView,
    PostViewSet,
    TagViewSet,
)

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("categories", CategoryViewSet, basename="category")
router.register("tags", TagViewSet, basename="tag")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "posts/<slug:post_slug>/comments/",
        PostCommentListCreateView.as_view(),
        name="post-comments",
    ),
]
