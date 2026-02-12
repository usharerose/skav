.PHONY: clean-pyc setup

build: clean-pyc
	docker compose build vibehist-build

run: build clean-container
	docker compose up -d vibehist-run

ssh:
	docker compose exec vibehist-run /bin/sh

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

clean-pyc:
	# clean all pyc files
	find . -name '__pycache__' | xargs rm -rf | cat
	find . -name '*.pyc' | xargs rm -f | cat

clean-container:
	# stop and remove useless containers
	docker compose down --remove-orphans
