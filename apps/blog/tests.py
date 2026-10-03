from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.blog.models import Category, Comment, Post


class BlogApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.author = user_model.objects.create_user(
            username="author",
            email="author@example.com",
            password="Strong-test-password-123",
        )
        self.other_user = user_model.objects.create_user(
            username="reader",
            email="reader@example.com",
            password="Strong-test-password-123",
        )
        self.category = Category.objects.create(name="News", slug="news")
        self.published_post = Post.objects.create(
            author=self.author,
            title="Published post",
            slug="published-post",
            body="Public content",
            status=Post.Status.PUBLISHED,
        )
        self.draft_post = Post.objects.create(
            author=self.author,
            title="Draft post",
            slug="draft-post",
            body="Private content",
        )

    def test_anonymous_users_only_see_published_posts(self):
        response = self.client.get("/api/posts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [post["slug"] for post in response.data],
            ["published-post"],
        )

    def test_homepage_redirects_to_api_root(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], "/api/")

    def test_api_root_lists_routes(self):
        response = self.client.get("/api/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("posts", response.data)
        self.assertIn("categories", response.data)
        self.assertIn("tags", response.data)

    def test_authenticated_author_can_create_post(self):
        self.client.force_authenticate(user=self.author)

        response = self.client.post(
            "/api/posts/",
            {
                "title": "New post",
                "slug": "new-post",
                "body": "Post body",
                "category": self.category.pk,
                "status": Post.Status.PUBLISHED,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(slug="new-post")
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.category, self.category)

    def test_author_can_see_own_drafts_but_other_users_cannot(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get("/api/posts/draft-post/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_author_cannot_edit_published_post(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            "/api/posts/published-post/",
            {"title": "Changed title"},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_creation_requires_authentication(self):
        response = self.client.post(
            "/api/posts/published-post/comments/",
            {"body": "A comment"},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Comment.objects.count(), 0)

    def test_authenticated_user_can_comment_on_published_post(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            "/api/posts/published-post/comments/",
            {"body": "A comment"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get()
        self.assertEqual(comment.author, self.other_user)
        self.assertEqual(comment.post, self.published_post)

    def test_jwt_token_can_be_obtained_with_existing_username(self):
        response = self.client.post(
            "/api/auth/token/",
            {"username": "author", "password": "Strong-test-password-123"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_registration_creates_user_with_hashed_password(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "new-user",
                "email": "new-user@example.com",
                "password": "Strong-test-password-123",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = get_user_model().objects.get(username="new-user")
        self.assertTrue(new_user.check_password("Strong-test-password-123"))
