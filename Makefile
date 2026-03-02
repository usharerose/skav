.PHONY: clean-pyc setup

build: clean-pyc
	docker compose build skav-build

run: build clean-container
	docker compose up -d skav-run

ssh:
	docker compose exec skav-run /bin/sh

setup:
	@command -v poetry >/dev/null 2>&1 || { \
		echo "Poetry is not installed. Please install it first:"; \
		echo "  curl -sSL https://install.python-poetry.org | python3 -"; \
		echo "  or"; \
		echo "  pip install poetry"; \
		exit 1; \
	}
	poetry update
	@echo ""
	@echo "✅ Setup complete!"
	@echo "   Run 'source .venv/bin/activate' to enter the virtual environment"

type-check:
	@echo "Run 'source .venv/bin/activate' to enter the virtual environment"
	mypy skav/ tests/

test:
	@echo "Run 'source .venv/bin/activate' to enter the virtual environment"
	pytest -sv tests/

lint:
	@echo "Run 'source .venv/bin/activate' to enter the virtual environment"
	ruff check .

prettier:
	@echo "Run 'source .venv/bin/activate' to enter the virtual environment"
	ruff format --check .

clean-pyc:
	# clean all pyc files
	find . -name '__pycache__' | xargs rm -rf | cat
	find . -name '*.pyc' | xargs rm -f | cat

clean-container:
	# stop and remove useless containers
	docker compose down --remove-orphans
