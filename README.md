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

## API routes

- `GET /api/posts/` and `GET /api/posts/<slug>/` — list and view published
  posts. Authenticated users can also see their own drafts.
- `POST /api/posts/` — create a post as the authenticated user.
- `PUT`, `PATCH`, and `DELETE /api/posts/<slug>/` — manage your own posts.
- `GET /api/categories/` and `GET /api/tags/` — list categories and tags.
- `GET /api/posts/<slug>/comments/` — list comments on a published post.
- `POST /api/posts/<slug>/comments/` — add a comment as an authenticated user.
- `POST /api/auth/register/` — register a user with `username`, `email`, and
  `password`.
- `POST /api/auth/token/` and `POST /api/auth/token/refresh/` — obtain and
  refresh JWTs. Token login uses the existing Django `username` and `password`.

Send authenticated requests with `Authorization: Bearer <access-token>`.
Public users can read published content; creating and changing content requires
authentication.

Run the API tests with:

```powershell
python manage.py test apps.blog
```