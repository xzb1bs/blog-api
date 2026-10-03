from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly

from apps.blog.models import Category, Comment, Post, Tag
from apps.blog.permissions import IsAuthorOrReadOnly
from apps.blog.serializers import (
    CategorySerializer,
    CommentSerializer,
    PostSerializer,
    TagSerializer,
    UserRegistrationSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    lookup_field = "slug"

    def get_queryset(self):
        posts = Post.objects.select_related("author", "category").prefetch_related("tags")
        if not self.request.user.is_authenticated:
            return posts.filter(status=Post.Status.PUBLISHED).order_by("-created_at")
        if self.action == "list":
            return posts.filter(
                Q(status=Post.Status.PUBLISHED) | Q(author=self.request.user)
            ).order_by("-created_at")
        return posts.filter(
            Q(status=Post.Status.PUBLISHED) | Q(author=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.order_by("name")
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.order_by("name")
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class PostCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_post(self):
        return get_object_or_404(
            Post,
            slug=self.kwargs["post_slug"],
            status=Post.Status.PUBLISHED,
        )

    def get_queryset(self):
        return Comment.objects.filter(post=self.get_post()).select_related("author")

    def perform_create(self, serializer):
        serializer.save(post=self.get_post(), author=self.request.user)


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)
