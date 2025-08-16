.PHONY: doctor lint test deploy bless clean

doctor:
	@echo "[doctor] Checking environment..."
	@python --version
	@pip list | grep Flask || echo "Flask not installed"

lint:
	@echo "[lint] Running flake8..."
	@flake8 app

test:
	@echo "[test] Running tests..."
	@pytest tests

deploy:
	@echo "[deploy] Deploying..."
	@git push origin main

bless:
	@echo "[bless] Refactoring..."
	@python bless_refactor.py

clean:
	@echo "[clean] Cleaning up..."
	@git clean -xdf
	@find . -name '__pycache__' -exec rm -r {} +
