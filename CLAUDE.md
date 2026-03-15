# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pekata ATS — a multi-tenant Applicant Tracking System built with Django. Manages job positions, candidates, interviews, case studies, and AI-powered evaluations. Supports Spanish, English, and Catalan with AI-driven translations via Claude.

## Commands

```bash
# Local development
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Docker (includes PostgreSQL, Redis, Celery)
docker-compose up

# Celery worker & beat scheduler
celery -A config worker -l info
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Tests (pytest configured, no test files yet)
pytest

# Static files for production
python manage.py collectstatic

# Management commands
python manage.py translate_existing   # Backfill translations for existing records
python manage.py load_media           # Load media files
```

## Architecture

### Multi-Tenant System
- `TenantMiddleware` in `apps/core/middleware.py` attaches the active company to every request
- Users belong to multiple companies via `CompanyMembership` (with Admin/Recruiter roles)
- Active company is stored in the session; all queries should be scoped to it

### Base Models (`apps/core/models.py`)
- **TimeStampedModel**: UUID primary key + created_at/updated_at — all models inherit from this
- **SoftDeleteMixin**: Adds deleted_at field. `objects` manager excludes soft-deleted; `all_objects` includes all

### App Structure (`apps/`)
- **core**: Auth, dashboard, AI services (`call_claude()`), Celery translation tasks, middleware
- **tenants**: Company, Department, CompanyMembership, UserSettings models
- **positions**: Job openings with employment types, statuses, AI-generated descriptions
- **candidates**: Applicants with CV upload, PDF text extraction, AI scoring
- **interviews**: Scheduling with Google Calendar integration
- **casestudies**: Case study assignments and candidate submissions
- **evaluations**: AI-powered candidate scoring (CV + interview + case study)
- **portal**: Public-facing candidate portal for case study submission
- **chatbot**: Two-step AI chatbot (route question → answer from knowledge base in `/knowledge/`)
- **notifications**: In-app notification system with JS polling

### AI Integration
- `apps/core/services.py` contains `call_claude()` — central function for all LLM calls
- Haiku for translations (cost-effective), Sonnet for complex analysis (evaluations, CV parsing)
- Async translation via Celery task `translate_instance_fields`

### Internationalization
- django-modeltranslation: model fields have `_es`, `_en`, `_ca` variants
- `UserLanguageMiddleware` activates user's preferred language per request
- Default language: Spanish (`es`)

### Frontend
- Server-rendered Django templates — no SPA, no JS build step
- Tailwind CSS + Alpine.js + Driver.js (all via CDN)
- Base layout: `templates/base.html`
- Chatbot widget: `static/js/chatbot.js` + `static/css/chatbot.css`

## Deployment

- **Platform**: Railway.app (config in `railway.toml`, `Procfile`)
- **Processes**: web (gunicorn, 2 workers, 120s timeout), worker (celery), beat (celery-beat)
- **Database**: PostgreSQL (production), SQLite (development)
- **Static files**: WhiteNoise; media via S3 in production
- **Docker**: `Dockerfile` (Python 3.12-slim) + `docker-compose.yml`

## Key Configuration

- Django settings: `config/settings.py`
- Root URLs: `config/urls.py`
- Celery config: `config/celery.py`
- Environment variables: see `.env.example`
