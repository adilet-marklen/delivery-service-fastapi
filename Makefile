.PHONY: up down logs run test tests lint format migrate makemigrations shell celery-worker celery-beat \
        dtest dlint dformat dmigrate dmakemigrations dshell dcelery-worker dcelery-beat compose-up compose-down

MESSAGE ?= "auto migration"

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

run:
	poetry run uvicorn delivery_service.main:app --reload --host 0.0.0.0 --port 8000

test:
	poetry run pytest

tests: test

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

migrate:
	poetry run alembic upgrade head

makemigrations:
	poetry run alembic revision --autogenerate -m $(MESSAGE)

shell:
	poetry run python

celery-worker:
	poetry run celery -A delivery_service.tasks.celery_app.celery_app worker -l info

celery-beat:
	poetry run celery -A delivery_service.tasks.celery_app.celery_app beat -l info

dtest:
	docker compose exec app poetry run pytest

dlint:
	docker compose exec app poetry run ruff check .

dformat:
	docker compose exec app poetry run ruff format .

dmigrate:
	docker compose exec app poetry run alembic upgrade head

dmakemigrations:
	docker compose exec app poetry run alembic revision --autogenerate -m $(MESSAGE)

dshell:
	docker compose exec app poetry run python

dcelery-worker:
	docker compose exec celery-worker celery -A delivery_service.tasks.celery_app.celery_app worker -l info

dcelery-beat:
	docker compose exec celery-beat celery -A delivery_service.tasks.celery_app.celery_app beat -l info

compose-up: up

compose-down: down
