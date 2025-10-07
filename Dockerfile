FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Install Python dependencies
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false && poetry install --without dev --no-interaction --no-ansi

# Copy project
COPY . /app/

# Run migrations and collect static files
RUN python manage.py collectstatic --noinput

# Expose port (for web interface if needed)
EXPOSE 8000

# Run the bot by default
CMD ["python", "run_bot.py"]
