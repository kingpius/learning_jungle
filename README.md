# Learning Jungle (MVP)

Learning Jungle is a Django web app for parents to manage child profiles and run a short diagnostic quiz (Maths) that produces a score, rank, and treasure unlock outcome.

## What it provides

- **Parent accounts**: register, login, logout
- **Child profiles (CRUD)**: create, view list, edit, delete
- **Diagnostic flow**: start → answer questions → submit → results (score + rank + treasure state)
- **Design system**: shared CSS primitives for consistent, child-friendly UI

## Tech stack

- Django (server-rendered templates)
- Postgres (production) / SQLite (local default)
- WhiteNoise (static files in production)
- Gunicorn (WSGI server)
- Optional AI integration (Gemini) for question generation

## Local setup

Create and activate a virtualenv, then install dependencies:

```
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Run migrations and start the server:

```
python manage.py migrate
python manage.py runserver
```

Run tests:

```
python manage.py test
```

## Environment variables (names only)

Minimum (production):
- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DATABASE_URL`

### Example formats (Heroku)

Use comma-separated values where applicable.

```
DEBUG=False
ALLOWED_HOSTS=learningjungle-d6ad829e4a2c.herokuapp.com
CSRF_TRUSTED_ORIGINS=https://learningjungle-d6ad829e4a2c.herokuapp.com
```

Gemini AI (optional):
- `AI_PROVIDER_URL`
- `AI_API_KEY`
- `AI_TIMEOUT_SECONDS`
- `AI_FALLBACK_MODE`

## Deployment (Heroku)

See `DEPLOYMENT.md` for Heroku setup steps, config vars, and smoke-test checklist.

## Troubleshooting (common deploy issues)

- **CSRF_TRUSTED_ORIGINS error**: ensure each entry starts with `https://` and matches your Heroku app domain.
- **DisallowedHost**: ensure `ALLOWED_HOSTS` includes your `<app>.herokuapp.com` domain.
- **Missing SECRET_KEY**: production requires `SECRET_KEY` set in environment variables.
- **AI errors**: verify `AI_PROVIDER_URL` points at the Gemini `generateContent` endpoint and `AI_API_KEY` is valid.

## Attribution

This project uses open-source libraries via `pip`:
- Django
- WhiteNoise
- Gunicorn
- dj-database-url
- psycopg2-binary

AI integration uses Google Gemini via HTTPS calls (no SDK), configured via environment variables.
