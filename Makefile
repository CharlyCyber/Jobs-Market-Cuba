.PHONY: help install test run clean docker-build docker-run docker-stop lint format

help:
	@echo "Cuba Jobs Telegram Bot - Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make run           - Run the bot"
	@echo "  make clean         - Clean cache files"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run with Docker Compose"
	@echo "  make docker-stop   - Stop Docker containers"
	@echo "  make lint          - Run linting"
	@echo "  make format        - Format code"

install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "Done!"

test:
	@echo "Running tests..."
	pytest -v
	@echo "Tests completed!"

run:
	@echo "Starting bot..."
	python run.py

clean:
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete!"

docker-build:
	@echo "Building Docker image..."
	docker-compose build
	@echo "Build complete!"

docker-run:
	@echo "Starting bot with Docker..."
	docker-compose up -d
	@echo "Bot is running! Use 'docker-compose logs -f' to see logs"

docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down
	@echo "Containers stopped!"

lint:
	@echo "Running linting..."
	@if command -v pylint > /dev/null; then \
		pylint bot scrapers filters; \
	else \
		echo "pylint not installed. Install with: pip install pylint"; \
	fi

format:
	@echo "Formatting code..."
	@if command -v black > /dev/null; then \
		black bot scrapers filters tests; \
	else \
		echo "black not installed. Install with: pip install black"; \
	fi
