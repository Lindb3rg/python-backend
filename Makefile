.PHONY: [install test format lint dev]

install:
	pip install -e .[dev]

test:
	pytest tests/ -v

format:
	@echo "Formatting code with Black..."
	black .
	@echo "Code formatted successfully!"

lint:
	flake8 .

dev: format lint test
	@echo "✅ All checks passed!"

rundev:
	fastapi dev  app/app.py