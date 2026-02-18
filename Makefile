run:
	uvicorn delivery_service.main:app --reload --host 0.0.0.0 --port 8000

tests:
	pytest

lint:
	ruff check .

format:
	ruff format .

compose-up:
	docker-compose up --build

compose-down:
	docker-compose down -v

