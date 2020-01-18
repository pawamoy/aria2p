.DEFAULT_GOAL := help

PY_SRC := src/ tests/ scripts/*.py

.PHONY: build
build:  ## Build sdist and wheel.
	poetry build

.PHONY: bundle
bundle:  ## Build one-file executable.
	poetry run bash -c 'pyinstaller -F -n aria2p -p $$VIRTUAL_ENV/lib/python3.6/site-packages src/aria2p/__main__.py'

.PHONY: clean
clean: clean-tests  ## Delete temporary files.
	@rm -rf build 2>/dev/null
	@rm -rf dist 2>/dev/null
	@rm -rf src/aria2p.egg-info 2>/dev/null
	@rm -rf .coverage* 2>/dev/null
	@rm -rf .pytest_cache 2>/dev/null
	@rm -rf pip-wheel-metadata 2>/dev/null

.PHONY: clean-tests
clean-tests:  ## Delete temporary tests files.
	@rm -rf tests/tmp/* 2>/dev/null

.PHONY: clear-queue
clear-queue:  ## Remove all downloads from the queue.
	poetry run aria2p remove -a

.PHONY: credits
credits:  ## Regenerate CREDITS.md.
	poetry run ./scripts/gen-credits-data.py | \
		poetry run jinja2 --format=json scripts/templates/CREDITS.md - -o CREDITS.md

.PHONY: docs
docs:  ## Build the documentation locally.
	poetry run sphinx-build -E -b html docs build/docs

.PHONY: help
help:  ## Print this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: check
check: check-bandit check-black check-flake8 check-isort check-safety check-ports  ## Check it all!

.PHONY: check-bandit
check-bandit:  ## Check for security warnings in code using bandit.
	poetry run bandit -r src/

.PHONY: check-black
check-black:  ## Check if code is formatted nicely using black.
	poetry run black --check $(PY_SRC)

.PHONY: check-flake8
check-flake8:  ## Check for general warnings in code using flake8.
	poetry run flake8 $(PY_SRC)

.PHONY: check-isort
check-isort:  ## Check if imports are correctly ordered using isort.
	poetry run isort -c -rc $(PY_SRC)

.PHONY: check-ports
check-ports:  ## Check if the ports used in the tests are all unique.
	poetry run python scripts/ports.py check

.PHONY: check-pylint
check-pylint:  ## Check for code smells using pylint.
	poetry run pylint $(PY_SRC)

.PHONY: check-safety
check-safety:  ## Check for vulnerabilities in dependencies using safety.
	poetry run pip freeze 2>/dev/null | \
		grep -v aria2p | \
		poetry run safety check --stdin --full-report 2>/dev/null

.PHONY: lint
lint: lint-black lint-isort  ## Run linting tools on the code.

.PHONY: lint-black
lint-black:  ## Lint the code using black.
	poetry run black $(PY_SRC)

.PHONY: lint-isort
lint-isort:  ## Sort the imports using isort.
	poetry run isort -y -rc $(PY_SRC)

.PHONY: load-queue
load-queue:  ## Load fixture downloads in the queue.
	poetry run aria2p add-magnets -f tests/data/linux_magnets

.PHONY: publish
publish:  ## Publish latest built version to PyPI.
	poetry publish

.PHONY: readme
readme:  ## Regenerate README.md.
	poetry run ./scripts/gen-readme-data.py | \
		poetry run jinja2 --format=json scripts/templates/README.md - -o README.md

.PHONY: setup
setup:  ## Setup the project with poetry.
	if ! command -v poetry; then \
	  command -v pipx && pipx install poetry || curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python; \
	fi
	poetry install -E tui

.PHONY: test
test: check-ports clean-tests  ## Run the tests using pytest.
	poetry run pytest -nauto -k "$(K)" 2>/dev/null
	-poetry run coverage html --rcfile=coverage.ini
	-poetry run coverage json --rcfile=coverage.ini
