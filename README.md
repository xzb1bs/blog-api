# blog-api

## Run locally

Activate the virtual environment and apply migrations:

```powershell
.\venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

The root URL redirects to the browsable API index at `/api/`. The Django admin
is available at `/admin/`.

Login uses **email**, not username. The user model is `apps.auths.User`.

## API routes

- `GET /api/posts/` and `GET /api/posts/<slug>/` — list and view published
  posts. Authenticated users can also see their own drafts.
- `POST /api/posts/` — create a post as the authenticated user.
- `PUT`, `PATCH`, and `DELETE /api/posts/<slug>/` — manage your own posts.
- `GET /api/categories/` and `GET /api/tags/` — list categories and tags.
- `GET /api/posts/<slug>/comments/` — list comments on a published post.
- `POST /api/posts/<slug>/comments/` — add a comment as an authenticated user.
- `POST /api/auth/register/` — register a user with `email`, `first_name`,
  `last_name`, and `password`.
- `POST /api/auth/token/` and `POST /api/auth/token/refresh/` — obtain and
  refresh JWTs. Token login uses `email` and `password`.

Send authenticated requests with `Authorization: Bearer <access-token>`.
Public users can read published content; creating and changing content requires
authentication.

Run the API tests with:

python manage.py test apps.blog



 Seeding

Fill the database with fake data (users, categories, tags, posts, comments):

python manage.py seed


Seed example
  
users:    20 created
categories:     8 created
tags:     9 created
posts:   100 created
comments:   200 created
Seeding completed in 1.55 seconds


All seeded users have the same password, stored in the `SEED_PASSWORD`
constant in `apps/blog/management/commands/seed.py`.
Running the command twice in a row is safe: existing emails, slugs,
categories and tags are skipped.


Admin
On an empty database:
python manage.py migrate
python manage.py seed
python manage.py createsuperuser
python manage.py runserver


Then open http://127.0.0.1:8000/admin/


Screenshots in the docs folder
