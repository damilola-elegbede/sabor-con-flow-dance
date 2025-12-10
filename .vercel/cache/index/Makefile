# Makefile for Sabor Con Flow Dance - Platform Engineering Development
# Optimized for local development workflow

.PHONY: help install install-dev setup clean test coverage run migrate collectstatic shell check format lint security

# Configuration
PYTHON := python3
PIP := pip
MANAGE := $(PYTHON) manage.py
DEV_SETTINGS := --settings=sabor_con_flow.settings_dev

# Default target
help:  ## Show this help message
	@echo "Sabor Con Flow Dance - Development Commands"
	@echo "==========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation and Setup
install:  ## Install production dependencies
	$(PIP) install -r requirements.txt

install-dev:  ## Install development dependencies
	$(PIP) install -r requirements-dev.txt

setup: install-dev migrate collectstatic  ## Full development setup
	@echo "🚀 Development environment setup complete!"
	@echo "Run 'make run' to start the development server"

venv:  ## Create virtual environment
	$(PYTHON) -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "source venv/bin/activate"

# Database Management
migrate:  ## Run database migrations
	$(MANAGE) migrate $(DEV_SETTINGS)

makemigrations:  ## Create new migrations
	$(MANAGE) makemigrations $(DEV_SETTINGS)

reset-db:  ## Reset development database
	rm -f db_dev.sqlite3
	$(MAKE) migrate

# Static Files
collectstatic:  ## Collect static files
	$(MANAGE) collectstatic --noinput $(DEV_SETTINGS)

# Development Server
run:  ## Start development server
	$(PYTHON) dev.py

run-simple:  ## Start development server (basic Django runserver)
	$(MANAGE) runserver $(DEV_SETTINGS)

run-production:  ## Start production-like server
	$(MANAGE) runserver --insecure $(DEV_SETTINGS)

# Development Tools
shell:  ## Open Django shell
	$(MANAGE) shell_plus $(DEV_SETTINGS) || $(MANAGE) shell $(DEV_SETTINGS)

createsuperuser:  ## Create superuser
	$(MANAGE) createsuperuser $(DEV_SETTINGS)

# Testing
test:  ## Run tests
	$(MANAGE) test $(DEV_SETTINGS) --verbosity=2

test-fast:  ## Run tests with parallel execution
	pytest --maxfail=1 -x -v

test-coverage:  ## Run tests with coverage
	coverage run --source='.' $(MANAGE) test $(DEV_SETTINGS)
	coverage report
	coverage html

coverage:  ## Generate and show coverage report
	coverage run $(MANAGE) test $(DEV_SETTINGS)
	coverage report -m
	coverage html
	@echo "Coverage report available at htmlcov/index.html"

# Code Quality
check:  ## Run Django system checks
	$(MANAGE) check $(DEV_SETTINGS)
	$(MANAGE) check --deploy $(DEV_SETTINGS)

format:  ## Format code with black and isort
	black .
	isort .

lint:  ## Run linting with flake8
	flake8 .

type-check:  ## Run type checking with mypy
	mypy .

quality: format lint type-check  ## Run all code quality checks

# Security and Performance
security:  ## Run security checks
	$(MANAGE) check --deploy $(DEV_SETTINGS)
	bandit -r . -f json -o security-report.json || true
	@echo "Security report generated: security-report.json"

performance:  ## Run performance checks
	$(MANAGE) check --deploy $(DEV_SETTINGS)
	@echo "Performance optimization suggestions:"
	@echo "1. Enable caching in production"
	@echo "2. Use CDN for static files"
	@echo "3. Enable database query optimization"

# Maintenance
clean:  ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/
	rm -f django_dev.log django.log
	@echo "Cleaned up temporary files"

clean-cache:  ## Clear Django cache
	$(MANAGE) clearsessions $(DEV_SETTINGS)
	@echo "Django cache cleared"

reset: clean reset-db setup  ## Complete reset of development environment

# Development Utilities
urls:  ## Show all URL patterns
	$(MANAGE) show_urls $(DEV_SETTINGS) || $(PYTHON) dev.py --urls

dbshell:  ## Open database shell
	$(MANAGE) dbshell $(DEV_SETTINGS)

logs:  ## Show recent logs
	tail -f django_dev.log || tail -f django.log

# Build and Deployment
build:  ## Build static assets
	npm run build || echo "No npm build configured"
	$(MAKE) collectstatic

deploy-check:  ## Check deployment readiness
	$(MANAGE) check --deploy --settings=sabor_con_flow.settings
	@echo "Deployment check complete"

# Monitoring and Health
health:  ## Check application health
	curl -f http://127.0.0.1:8000/health/ || echo "Server not running"

monitor:  ## Show monitoring dashboard URLs
	@echo "Monitoring URLs (server must be running):"
	@echo "Health Check:    http://127.0.0.1:8000/health/"
	@echo "Admin Dashboard: http://127.0.0.1:8000/admin/"
	@echo "DB Performance:  http://127.0.0.1:8000/admin/db-performance/"

# Docker Support (if needed later)
docker-build:  ## Build Docker image
	docker build -t sabor-con-flow-dev .

docker-run:  ## Run in Docker container
	docker run -p 8000:8000 sabor-con-flow-dev

# Backup and Restore
backup:  ## Backup development database
	cp db_dev.sqlite3 db_dev.sqlite3.backup.$(shell date +%Y%m%d_%H%M%S)
	@echo "Database backed up"

restore:  ## List available backups
	@echo "Available backups:"
	@ls -la db_dev.sqlite3.backup.* 2>/dev/null || echo "No backups found"

# Quick Development Commands
dev: setup run  ## Quick setup and run
fresh: reset run  ## Fresh install and run
quick: migrate collectstatic run  ## Quick restart