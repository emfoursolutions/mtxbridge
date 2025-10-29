# ABOUTME: Makefile with common development commands
# ABOUTME: Provides shortcuts for testing, linting, and deployment tasks

.PHONY: help install dev-install test lint format clean run docker-build docker-up docker-down init-db create-admin init-sqlite

help:
	@echo "Available commands:"
	@echo "  make install           - Install production dependencies"
	@echo "  make dev-install       - Install development dependencies"
	@echo "  make test              - Run all tests"
	@echo "  make lint              - Run linters"
	@echo "  make format            - Format code with black"
	@echo "  make clean             - Remove build artifacts"
	@echo "  make run               - Run development server"
	@echo "  make docker-build      - Build Docker images"
	@echo "  make docker-up         - Start Docker services (PostgreSQL)"
	@echo "  make docker-up-sqlite  - Start Docker services (SQLite)"
	@echo "  make docker-down       - Stop Docker services"
	@echo "  make init-db           - Initialize database"
	@echo "  make init-sqlite       - Initialize SQLite database (quick start)"
	@echo "  make create-admin      - Create admin user"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest

test-unit:
	pytest tests/unit/

test-integration:
	pytest tests/integration/

test-e2e:
	pytest tests/e2e/

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

lint:
	ruff check app/ tests/
	mypy app/

format:
	black app/ tests/
	ruff check --fix app/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info

run:
	python app.py

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-up-sqlite:
	docker-compose -f docker-compose.sqlite.yml up -d

docker-down:
	docker-compose down
	docker-compose -f docker-compose.sqlite.yml down 2>/dev/null || true

docker-logs:
	docker-compose logs -f

docker-logs-sqlite:
	docker-compose -f docker-compose.sqlite.yml logs -f

init-db:
	python manage.py init-db

init-sqlite:
	python init_sqlite.py

create-admin:
	@read -p "Enter username: " username; \
	python manage.py create-admin $$username
