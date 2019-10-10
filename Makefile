.DEFAULT_GOAL := help

PY_SRC := src/ tests/ scripts/*.py docs/conf.py
SH_SRC := scripts/*.sh

.PHONY: help
help:  ## Print this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: readme
readme:  ## Regenerate README.md.
	poetry run ./scripts/gen-readme-data.py | \
		poetry run jinja2 --format=json scripts/templates/README.md - -o README.md

.PHONY: credits
credits:  ## Regenerate CREDITS.md.
	poetry run ./scripts/gen-credits-data.py | \
		poetry run jinja2 --format=json scripts/templates/CREDITS.md - -o CREDITS.md

.PHONY: docs
docs:  ## Build the documentation locally.
	poetry run sphinx-build -E -b html docs build/docs

.PHONY: check
check: check-bandit check-black check-flake8 check-isort check-safety check-ports check-docs-spelling  ## Check it all!

.PHONY: update-spelling-wordlist
update-spelling-wordlist:  ## Update the spelling word list.
	scripts/update-spelling-wordlist.sh

.PHONY: check-docs-spelling
check-docs-spelling: update-spelling-wordlist  ## Check spelling in the documentation.
	scripts/check-docs-spelling.sh

.PHONY: check-black
check-black:  ## Check if code is formatted nicely using black.
	poetry run black --check $(PY_SRC)

.PHONY: check-isort
check-isort:  ## Check if imports are correctly ordered using isort.
	poetry run isort -c -rc $(PY_SRC)

.PHONY: check-flake8
check-flake8:  ## Check for general warnings in code using flake8.
	poetry run flake8 $(PY_SRC)

.PHONY: check-bandit
check-bandit:  ## Check for security warnings in code using bandit.
	poetry run bandit -r src/

.PHONY: check-safety
check-safety:  ## Check for vulnerabilities in dependencies using safety.
	poetry run pip freeze 2>/dev/null | \
		grep -v aria2p | \
		poetry run safety check --stdin --full-report 2>/dev/null

.PHONY: check-ports
check-ports:  ## Check if the ports used in the tests are all unique.
	scripts/check-ports.sh

.PHONY: check-pylint
check-pylint:  ## Check for code smells using pylint.
	poetry run pylint src/

.PHONY: run-black
run-black:  ## Lint the code using black.
	poetry run black $(PY_SRC)

.PHONY: run-isort
run-isort:  ## Sort the imports using isort.
	poetry run isort -y -rc $(PY_SRC)

.PHONY: lint
lint: run-black run-isort  ## Run linting tools on the code.

.PHONY: clean-tests
clean-tests:  ## Delete temporary tests files.
	@rm -rf tests/tmp/* 2>/dev/null

.PHONY: clean
clean: clean-tests  ## Delete temporary files.
	@rm -rf build 2>/dev/null
	@rm -rf dist 2>/dev/null
	@rm -rf src/aria2p.egg-info 2>/dev/null
	@rm -rf .coverage* 2>/dev/null
	@rm -rf .pytest_cache 2>/dev/null
	@rm -rf pip-wheel-metadata 2>/dev/null

.PHONY: test
test: check-ports clean-tests  ## Run the tests using pytest.
	poetry run pytest -n6 2>/dev/null
