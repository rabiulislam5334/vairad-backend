# Vairad Backend — Task Management & Image Annotation API

A Django REST Framework backend powering a 2-in-1 web application: a date-based Kanban task manager and an image annotation tool.Built with JWT authentication, SQLite for local development (easily swappable for PostgreSQL in production via Django's ORM), and a modular, permission-scoped API design.
---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Architecture Overview](#architecture-overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Challenges & Solutions](#challenges--solutions)
- [Future Improvements](#future-improvements)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 6.0 + Django REST Framework |
| Authentication | JWT (`djangorestframework-simplejwt`), email-based custom User model |
| Database | SQLite (development) — swappable for PostgreSQL/MySQL via `DATABASES` config |
| Filtering | `django-filter` |
| Image handling | Pillow |
| CORS | `django-cors-headers` |

---

## Architecture Overview

The project follows Django's app-based modular architecture, with each domain isolated into its own app:

```
accounts/       → Custom user model, JWT auth, permissions
tasks/          → Kanban task & tag models, CRUD API, drag-drop ordering
annotations/    → Image upload, polygon storage, annotation CRUD API
```

**Key design decisions:**

- **Email-based authentication** — the default Django `User` model was replaced with a custom model (`AUTH_USER_MODEL`) using email as the unique identifier instead of username, matching the login requirement in the spec.
- **Object-level ownership** — every task, tag, image, and polygon is scoped to the authenticated user via `get_queryset()` filtering *and* an explicit `IsOwner` permission class, so a user can never read or mutate another user's data even if they guess an object ID.
- **Serializer-level validation** — business rules (minimum title length, valid priority values, polygon point count, image type/size limits) are enforced in serializers rather than views, keeping validation reusable and testable independent of the HTTP layer.
- **Nested serialization** — annotation images return their polygons inline (`GET /api/annotate/images/:id/`), so the frontend can render an image with all its shapes in a single request.

---

## Features

### Authentication
- Email + password login issuing JWT access/refresh token pairs
- Token refresh endpoint
- `/me` endpoint for fetching the current authenticated user

### Task Management (Kanban)
- Full CRUD for tasks (title, description, priority, due date, tags, status)
- Filter tasks by `due_date` and `status` (powers the date-selector UI)
- Dedicated `move` endpoint for drag-and-drop — updates both column (`status`) and order in one call
- Many-to-many tagging system, scoped per user

### Image Annotation
- Multipart image upload with server-side type (`jpeg`/`png`/`webp`) and size (max 5MB) validation
- Polygon storage as JSON coordinate arrays (`[{x, y}, ...]`)
- Create and delete individual polygons per image
- Minimum 3-point validation (rejects degenerate/line-only shapes)

### Cross-cutting
- Pagination (10 items per page) on all list endpoints
- CORS configured for a Next.js frontend running on `localhost:3000`
- Django admin panel fully wired for all models

---

## Prerequisites

- **Python:** 3.13.x
- **pip:** latest (bundled with Python)
- OS: Windows / macOS / Linux (tested on Windows with PowerShell)

---

## Setup & Installation

```bash
# 1. Clone the repository
git clone https://github.com/rabiulislam5334/vairad-backend.git
cd vairad-backend

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
copy .env.example .env         # Windows
# cp .env.example .env         # macOS/Linux
# then edit .env and set SECRET_KEY / DEBUG

# 5. Run migrations
python manage.py migrate

# 6. Create an admin/demo user
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`, and the Django admin at `http://127.0.0.1:8000/admin/`.

---

## Environment Variables

Create a `.env` file in the project root (see `.env.example`):

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
```

`SECRET_KEY` and `DEBUG` are loaded via `python-dotenv` and must never be committed — `.env`, `db.sqlite3`, and `venv/` are excluded via `.gitignore`.

---

## API Reference

Base URL: `http://127.0.0.1:8000/api/`

### Auth (`/api/auth/`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/login/` | Login with email + password → returns `access`, `refresh`, `user` |
| POST | `/refresh/` | Exchange a refresh token for a new access token |
| GET | `/me/` | Return the authenticated user's profile |

### Tasks (`/api/`)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/tasks/` | List tasks (paginated, filterable by `due_date`, `status`) |
| POST | `/tasks/` | Create a task |
| GET | `/tasks/:id/` | Retrieve a task |
| PATCH | `/tasks/:id/` | Update a task |
| DELETE | `/tasks/:id/` | Delete a task |
| PATCH | `/tasks/:id/move/` | Update `status` and `order` (drag-and-drop) |
| GET / POST | `/tags/` | List / create tags |

### Annotations (`/api/annotate/`)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/images/` | List uploaded images (with nested polygons) |
| POST | `/images/` | Upload an image (`multipart/form-data`, field name `image`) |
| DELETE | `/images/:id/` | Delete an image (cascades to its polygons) |
| POST | `/polygons/` | Create a polygon (`image`, `label`, `color`, `points`) |
| DELETE | `/polygons/:id/` | Delete a specific polygon |

All endpoints except `/login/` and `/refresh/` require:
```
Authorization: Bearer <access_token>
```

---

## Project Structure

```
vairad-backend/
├── accounts/
│   ├── models.py          # Custom User model (email-based)
│   ├── serializers.py
│   ├── views.py            # Login, Me views
│   ├── permissions.py       # IsOwner permission
│   └── urls.py
├── tasks/
│   ├── models.py           # Task, Tag models
│   ├── serializers.py       # includes validation rules
│   ├── views.py             # TaskViewSet, TagViewSet, move action
│   └── urls.py
├── annotations/
│   ├── models.py            # AnnotationImage, Polygon models
│   ├── serializers.py        # includes upload/points validation
│   ├── views.py               # AnnotationImageViewSet, PolygonViewSet
│   └── urls.py
├── vairad_backend/
│   ├── settings.py
│   └── urls.py
├── requirements.txt
├── .env.example
└── manage.py
```

---

## Challenges & Solutions

**1. Email-based authentication with Django's default User model**
Django's built-in `User` model is username-first. Since the spec required email + password login, a custom `User` model extending `AbstractUser` was introduced early — before the first migration — since swapping `AUTH_USER_MODEL` after migrations exist requires resetting the database. This is documented as a Django gotcha; setting it up correctly from the start avoided a costly rework.

**2. File uploads silently hanging in the API client**
During manual testing, multipart image-upload requests sent through the REST client would hang indefinitely with no server-side log entry — indicating the request never reached Django. Testing the same request with `curl.exe` (bypassing PowerShell's `curl` alias, which maps to `Invoke-WebRequest` and doesn't support `-F`/`-H` flags) confirmed the backend was working correctly and isolated the issue to the client tooling rather than the API.

**3. Enforcing per-user data isolation beyond queryset filtering**
Filtering querysets by `request.user` protects list/read endpoints, but a user could still attempt to mutate another user's object by guessing its ID in a detail URL. A reusable `IsOwner` permission class was added, checked at the object level for every write operation across tasks, tags, images, and polygons — including nested objects like `Polygon`, which is owned indirectly through its parent image.

**4. Keeping validation logic out of views**
To avoid views growing complex conditional logic, validation rules (minimum title length, valid priority choices, polygon point count, image MIME type/size) were placed in serializer `validate_<field>` methods, keeping views focused purely on request/response orchestration.

---

## Future Improvements

- Split `settings.py` into `base/local/production` configurations for cleaner environment-specific deployment
- Add a `bulk_update()`-based endpoint for reordering multiple tasks in a single request (currently one `move` call per task)
- Swagger/OpenAPI documentation via `drf-spectacular`
- Unit test coverage for authentication, permissions, and CRUD flows
- Structured logging and a global exception handler for consistent error response shapes
- Docker Compose setup for one-command local development

---

## Author

**Rabiul Islam** — Full-Stack Developer
[GitHub](https://github.com/rabiulislam5334) · [LinkedIn](https://www.linkedin.com/in/developerrabiul)
