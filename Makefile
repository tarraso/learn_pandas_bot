.PHONY: help install migrate run createsuperuser shell test clean

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies using poetry"
	@echo "  make migrate        - Run Django migrations"
	@echo "  make run            - Run the Telegram bot"
	@echo "  make createsuperuser - Create Django superuser"
	@echo "  make shell          - Open Django shell"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean Python cache files"
	@echo "  make loaddata       - Load initial sample data"

install:
	poetry install

migrate:
	python manage.py makemigrations
	python manage.py migrate

run:
	python run_bot.py

createsuperuser:
	python manage.py createsuperuser

shell:
	python manage.py shell

test:
	pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete

loaddata:
	python manage.py loaddata initial_data.json

runserver:
	python manage.py runserver
