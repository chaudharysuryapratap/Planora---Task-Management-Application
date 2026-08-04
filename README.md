# Planora

Planora is a Flask task-management application with a server-rendered web interface and a JWT-protected REST API.

## Live Application

[🚀 Open Planora Live](http://planora.ap-southeast-2.elasticbeanstalk.com)

> The application is hosted on AWS Elastic Beanstalk with Amazon RDS PostgreSQL.

## Features

- User registration and login
- JWT access and refresh tokens
- Task creation, listing, filtering, search, status updates, assignment, and soft deletion
- Personal and default categories
- Profile and password updates
- Responsive server-rendered pages
- Request rate limiting and API validation

## Tech stack

- Python 3.9+
- Flask and Jinja
- Flask-SQLAlchemy and Flask-Migrate
- Flask-JWT-Extended
- Flask-Limiter
- Pydantic
- Passlib
- SQLite by default; MySQL and PostgreSQL are supported through SQLAlchemy URLs

## Local setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Planora
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements-dev.txt
```

For runtime-only dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configure the environment

Copy `.env.example` to `.env`, then replace both secret values.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS or Linux:

```bash
cp .env.example .env
```

Generate secrets with Python:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

The default database is SQLite. To use another database, set `DATABASE_URL` in `.env`.

### 5. Apply database migrations

```bash
flask --app run.py db upgrade
```

### 6. Start the application

```bash
python run.py
```

Open `http://localhost:5000`.

## Tests

```bash
pytest
```

## API overview

All API routes use the `/api/v1` prefix.

| Area | Endpoints |
|---|---|
| Authentication | `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me` |
| Users | `/users/me`, `/users/me/password` |
| Tasks | `/tasks`, `/tasks/search`, `/tasks/<id>`, `/tasks/<id>/status`, `/tasks/<id>/assign` |
| Categories | `/categories`, `/categories/<id>` |

Protected endpoints require:

```http
Authorization: Bearer <access-token>
```

## Project structure

```text
app/
├── middleware/     # JWT request authentication
├── models/         # SQLAlchemy models
├── routes/         # API and frontend routes
├── schemas/        # Pydantic request validation
├── services/       # Business logic
├── static/         # CSS, JavaScript, and images
└── templates/      # Jinja templates
migrations/         # Alembic migrations
tests/              # Automated tests
run.py              # Development entry point
```

## Security notes

- Never commit `.env`, database credentials, JWT secrets, or a virtual environment.
- Use different values for `SECRET_KEY` and `JWT_SECRET_KEY`.
- Disable Flask debug mode outside local development.
- Restrict `CORS_ORIGINS` to trusted browser origins.
- Use HTTPS and a persistent Flask-Limiter storage backend in production.

## Current limitations

- Task editing in the web interface is not finished, although the update API exists.
- Notification preferences, two-factor authentication, session management, and account deletion are presentation-only placeholders.
- Browser authentication currently uses tokens stored in `localStorage`. A production deployment should prefer secure, HttpOnly cookies with CSRF protection.
- The dashboard loads up to 100 tasks for client-side statistics.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
