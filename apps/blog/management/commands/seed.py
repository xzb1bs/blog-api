import random
import time
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction
from django.utils.text import slugify
from faker import Faker

from apps.blog.models import Category, Comment, Post, Tag


User = get_user_model()

default_users = 20
default_posts = 100
default_comments = 200

seed_password = "password"
email_domain = "example.com"

inactive_ratio = 0.1
staff_ratio = 0.1
published_ratio = 0.7
no_category_ratio = 0.1

min_paragraphs = 3
max_paragraphs = 6
max_tags_per_post = 5
min_comment_sentences = 1
max_comment_sentences = 3

status_published = "published"
status_draft = "draft"

category_names = [
    "django", "API", "python", "javascript", "react", "vue", "html", "css",
]

tag_names = [
    "tutorial", "docs", "tricks", "tips", "news", "release", "update",
    "feature", "bugfix",
]


class Command(BaseCommand):
    help = "Fill the database with fake data"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--users", type=int, default=default_users)
        parser.add_argument("--posts", type=int, default=default_posts)
        parser.add_argument("--comments", type=int, default=default_comments)
        parser.add_argument("--clear", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        start_time = time.time()
        users_count: int = options["users"]
        posts_count: int = options["posts"]
        comments_count: int = options["comments"]

        if min(users_count, posts_count, comments_count) < 0:
            raise CommandError("User, post and comment counts must not be negative")

        fake = Faker()
        with transaction.atomic():
            if options["clear"]:
                self.clear_data()

            users_created = self.create_users(fake, users_count)
            categories_created = self.create_names(Category, category_names)
            tags_created = self.create_names(Tag, tag_names)
            posts_created = self.create_posts(fake, posts_count)
            comments_created = self.create_comments(fake, comments_count)

        spent = time.time() - start_time
        self.stdout.write(f"users: {users_created:>5} created")
        self.stdout.write(f"categories: {categories_created:>5} created")
        self.stdout.write(f"tags: {tags_created:>5} created")
        self.stdout.write(f"posts: {posts_created:>5} created")
        self.stdout.write(f"comments: {comments_created:>5} created")
        self.stdout.write(self.style.SUCCESS(
            f"Seeding completed in {spent:.2f} seconds"
        ))

    def clear_data(self) -> None:
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write("Old data deleted (except superusers)")

    def create_users(self, fake: Faker, count: int) -> int:
        used_emails = set(User.objects.values_list("email", flat=True))
        hashed_password = make_password(seed_password)
        users = []

        while len(users) < count:
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name}.{last_name}@{email_domain}".lower().replace(" ", "")
            if email in used_emails:
                continue
            used_emails.add(email)
            users.append(User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=hashed_password,
                is_active=random.random() > inactive_ratio,
                is_staff=random.random() < staff_ratio,
            ))

        User.objects.bulk_create(users)
        return len(users)

    def create_names(self, model: type, names: list[str]) -> int:
        existing_names = set(model.objects.values_list("name", flat=True))
        objects = []
        for name in names:
            if name not in existing_names:
                objects.append(model(name=name, slug=slugify(name)))
        model.objects.bulk_create(objects)
        return len(objects)

    def create_posts(self, fake: Faker, count: int) -> int:
        if count == 0:
            return 0

        users = list(User.objects.all())
        if not users:
            raise CommandError("No users available to assign posts. Create users first.")

        categories = list(Category.objects.all())
        tags = list(Tag.objects.all())
        used_slugs = set(Post.objects.values_list("slug", flat=True))
        posts = []
        tags_for_posts = []

        for _ in range(count):
            title = fake.sentence(nb_words=6).rstrip(".")
            base_slug = slugify(title)
            slug = base_slug
            number = 2
            while slug in used_slugs:
                slug = f"{base_slug}-{number}"
                number += 1
            used_slugs.add(slug)

            status = status_published if random.random() < published_ratio else status_draft
            category = None if not categories or random.random() < no_category_ratio else random.choice(categories)
            paragraphs = fake.paragraphs(
                nb=random.randint(min_paragraphs, max_paragraphs)
            )
            post = Post(
                author=random.choice(users),
                category=category,
                title=title,
                slug=slug,
                body="\n\n".join(paragraphs),
                status=status,
            )
            posts.append(post)
            tags_amount = random.randint(0, min(max_tags_per_post, len(tags)))
            tags_for_posts.append((post, random.sample(tags, tags_amount)))

        Post.objects.bulk_create(posts)
        for post, tags_for_post in tags_for_posts:
            post.tags.set(tags_for_post)
        return len(posts)

    def create_comments(self, fake: Faker, count: int) -> int:
        if count == 0:
            return 0

        users = list(User.objects.all())
        published_posts = list(Post.objects.filter(status=status_published))
        posts = list(Post.objects.all()) if not published_posts else published_posts
        if not users:
            raise CommandError("No users available to assign comments. Create users first.")
        if not posts:
            raise CommandError("No posts available to assign comments. Create posts first.")

        comments = []
        for _ in range(count):
            sentences = fake.sentences(
                nb=random.randint(min_comment_sentences, max_comment_sentences)
            )
            comments.append(Comment(
                author=random.choice(users),
                post=random.choice(posts),
                body=" ".join(sentences),
            ))
        Comment.objects.bulk_create(comments)
        return len(comments)
