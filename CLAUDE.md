# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Learn Pandas Bot is a Telegram bot with a React-based mini-app for interactive Python/Pandas learning. The system combines:
- Django backend with REST API
- Telegram bot using python-telegram-bot
- React + Vite frontend (Telegram Mini App)
- In-browser Python execution via Pyodide

## Architecture

### Django Application Structure
The project uses a multi-app Django architecture:

- **`questions/`** - Core domain models: `Topic`, `Question`, `Snippet`
  - Questions support multiple types: multiple_choice, code, explanation, fill_blank
  - Each question has difficulty levels (beginner/intermediate/advanced)

- **`bot/`** - Telegram user management and progress tracking
  - Models: `TelegramUser`, `QuestionHistory`, `UserProgress`
  - `bot/utils.py` contains helper functions for bot operations

- **`api/`** - DRF REST API for the Mini App
  - `views_drf.py` provides ViewSets for topics, questions, code tasks
  - Endpoints used by React frontend

- **`webapp/`** - React + Vite Mini App
  - Monaco editor for code challenges
  - Pyodide for client-side Python execution
  - Telegram Web App SDK integration

### Key Integration Points

**Django Initialization for Standalone Scripts:**
All standalone scripts (like `run_bot.py`, `add_questions.py`) must import `init_django` first to initialize Django ORM:
```python
import init_django  # noqa
```

**Telegram Bot Entry Point:**
`run_bot.py` is the main bot process. It uses async/await with python-telegram-bot library v22+.

**API Communication:**
The Mini App communicates with Django backend through `/api/` endpoints, proxied through nginx in production.

## Common Development Commands

### Environment Setup
```bash
# Install dependencies
poetry install

# Copy and configure environment
cp .env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN and DATABASE_URL
```

### Database Operations
```bash
# Create and run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for Django admin
python manage.py createsuperuser

# Django shell
python manage.py shell
```

### Running the Application

**Telegram Bot:**
```bash
# Run the bot
python run_bot.py
# Or via make
make run
```

**Django Development Server (for admin/API):**
```bash
python manage.py runserver
# Or via make
make runserver
```

**Mini App Development:**
```bash
cd webapp
npm install
npm run dev  # Starts on localhost:5173
```

### Testing
```bash
# Run tests with pytest
pytest

# Via make
make test
```

### Mini App Build & Deployment
```bash
# Build for production
cd webapp
npm run build  # Output to webapp/dist/

# Deploy to server (from project root)
./scripts/deploy_miniapp.sh
```

### Utility Scripts
```bash
# Clean Python cache files
make clean

# Database backup (production)
./scripts/backup.sh

# Full deployment to VPS
./scripts/deploy.sh
```

## Database Schema Notes

### Key Relationships
- `Question` → `Topic` (many-to-one)
- `TelegramUser` → `Topic` (current_topic, many-to-one)
- `QuestionHistory` → `TelegramUser` + `Question` (tracks answers)
- `UserProgress` → `TelegramUser` + `Topic` (unique_together)

### Question Model Specifics
- For `multiple_choice`: uses `option_a` through `option_d`, with `correct_option` (A/B/C/D)
- For `code` challenges: uses `starter_code`, `test_cases` (JSON), `correct_answer`, and optional `hint`
- All questions have `explanation` and optional `documentation_link`

## Environment Configuration

Required environment variables (see `.env.example`):
- `TELEGRAM_BOT_TOKEN` - From @BotFather
- `DATABASE_URL` - SQLite for dev, PostgreSQL for production
- `SECRET_KEY` - Django secret key
- `WEBAPP_URL` - Mini app URL (production domain or ngrok for dev)
- `DEBUG` - Set to `False` in production

## Deployment Architecture

**Production Stack:**
- Ubuntu VPS with 512MB-1GB RAM (see MEMORY_OPTIMIZATION.md)
- Nginx reverse proxy serving Mini App static files + proxying API
- Gunicorn for Django backend
- Systemd service for Telegram bot (`pandas-bot.service`)
- PostgreSQL database

**Docker Options:**
- `docker-compose.yml` - Basic development setup
- `docker-compose.prod.yml` - Full production with nginx
- `docker-compose.prod.lite.yml` - Lighter production variant

## Code Patterns & Conventions

### Async Bot Handlers
All bot command handlers are async functions with signature:
```python
async def handler_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Always check if user exists
    if not user:
        return
    telegram_user, created = await get_or_create_user(user)
    # ...
```

### API Views (DRF)
Use ViewSets for model-based endpoints, APIView for custom logic:
```python
class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Topic.objects.all().order_by('order', 'name')
    serializer_class = TopicSerializer
```

### Django Settings
Settings are in `pandas_bot/settings.py` with environment-based configuration via `python-dotenv`. Uses `dj-database-url` for database URL parsing.

## Mini App Development Notes

**File Structure:**
- `webapp/src/components/` - React components (Monaco editor, task interface)
- `webapp/src/config.js` - API URL configuration (uses VITE_API_URL env var)
- `webapp/dist/` - Production build output (served by nginx)

**API Integration:**
The Mini App expects:
- `GET /api/code/task/?user_id={telegram_id}` - Fetch Python tasks
- `POST /api/code/submit/` - Submit code solutions

**Build Process:**
Vite build creates optimized bundles with hashed filenames for cache busting. Nginx config includes long-term caching headers for these assets.

## Testing Philosophy

Tests use pytest with pytest-django and pytest-asyncio plugins. The `pytest.ini` sets `DJANGO_SETTINGS_MODULE` and enables auto async mode.

## Adding Questions/Content

**Via Django Admin:**
1. Start dev server: `python manage.py runserver`
2. Visit http://localhost:8000/admin/
3. Add Topics, Questions, Code Snippets

**Via Scripts:**
- `add_questions.py` - Bulk add questions (requires `init_django`)
- `add_python_tasks.py` - Add Python coding tasks
- Both scripts use Django ORM directly

## Documentation References

- [DEPLOY.md](DEPLOY.md) - Full production deployment guide
- [MEMORY_OPTIMIZATION.md](MEMORY_OPTIMIZATION.md) - Running on low-memory VPS
- [MINIAPP_DEPLOY.md](MINIAPP_DEPLOY.md) - Mini App deployment specifics
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API endpoints documentation
- [webapp/README.md](webapp/README.md) - Frontend development guide
