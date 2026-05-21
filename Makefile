.PHONY: up down migrate test-backend logs

up:
	docker-compose up --build

down:
	docker-compose down -v

migrate:
	docker-compose exec backend alembic upgrade head

test-backend:
	docker-compose exec backend pytest tests/ -v

logs:
	docker-compose logs -f
