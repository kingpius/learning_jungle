# Deployment (Heroku) — LJ-009

This repo is configured for a simple Heroku deployment of the Learning Jungle MVP.

## Files used by Heroku

- `Procfile` — starts the web dyno via Gunicorn
- `runtime.txt` — pins the Python runtime
- `config/settings.py` — env-driven production settings, Postgres via `DATABASE_URL`, static via WhiteNoise

## Heroku setup (one-time)

1. Create the app:
   - `heroku create <app-name>`
2. Add Postgres:
   - `heroku addons:create heroku-postgresql`

## Config vars (names only)

Minimum:
- `SECRET_KEY`
- `DEBUG` (set to `False`)
- `ALLOWED_HOSTS` (comma-separated; must include `<app>.herokuapp.com`)
- `DATABASE_URL` (set automatically by Heroku Postgres)

Optional but recommended:
- `SECURE_HSTS_SECONDS` (defaults to `3600`)
- `LOG_LEVEL` (defaults to `INFO`)
- `CSRF_TRUSTED_ORIGINS` (comma-separated `https://...` origins, if needed)

AI (optional; app will not crash without these):
- `AI_PROVIDER_URL`
- `AI_API_KEY`
- `AI_MODEL`
- `AI_TIMEOUT_SECONDS`
- `AI_FALLBACK_MODE` (`stub` on Heroku by default; set to `error` to fail instead of stubbing)

## Deploy

1. Push code:
   - `git push heroku feature/LJ-009-deployment:main` (or your chosen branch)
2. Run migrations:
   - `heroku run python manage.py migrate`
3. Confirm static assets:
   - Heroku runs `collectstatic` at build time; verify core pages load CSS.

## Smoke test checklist (production URL)

- Home route loads (no 500s) and CSS is applied.
- Parent auth: register/login/logout.
- Child diagnostic: start → answer → submit → results.
- Completed diagnostic revisit: read-only (redirects to results).
- AI path: either configured and works, or safely falls back (no crash).

