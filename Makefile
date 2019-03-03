.PHONY: help
.PHONY: docs
.PHONY: test-py36
.PHONY: test-py37
.PHONY: clean
.PHONY: clean-tests
.DEFAULT_GOAL := help

help:  ## Print this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

readme: README.md  ## Regenerate README.md.
	poetry run ./scripts/gen-readme-data.py | \
		poetry run jinja2 --format=json scripts/templates/README.md > README.md

docs:  ## Build the documentation locally.
	poetry run sphinx-build -E -b html docs build/docs

check: check-bandit check-black check-flake8 check-isort check-safety check-ports check-docs-spelling  ## Check it all!

update-spelling-wordlist:  ## Update the spelling word list.
	scripts/update-spelling-wordlist.sh

check-docs-spelling: update-spelling-wordlist  ## Check spelling in the documentation.
	scripts/check-docs-spelling.sh

check-black:  ## Check if code is formatted nicely using black.
	poetry run black --check src/ tests/ docs/conf.py

check-isort:  ## Check if imports are correctly ordered using isort.
	poetry run isort -c -rc src/ tests/ docs/conf.py

check-flake8:  ## Check for general warnings in code using flake8.
	poetry run flake8 src/ tests/

check-bandit:  ## Check for security warnings in code using bandit.
	poetry run bandit -r src/

check-safety:  ## Check for vulnerabilities in dependencies using safety.
	poetry run pip freeze 2>/dev/null | \
		grep -v aria2p | \
		poetry run safety check --stdin --full-report 2>/dev/null

check-ports:  ## Check if the ports used in the tests are all unique.
	scripts/check-ports.sh

run-black:  ## Lint the code using black.
	poetry run black src/ tests/ docs/conf.py

run-isort:  ## Sort the imports using isort.
	poetry run isort -y -rc src/ tests/ docs/conf.py

lint: run-black run-isort  ## Run linting tools on the code.

clean-tests:  ## Delete temporary tests files.
	@rm -rf tests/tmp/* 2>/dev/null

clean: clean-tests  ## Delete temporary files.
	@rm -rf build 2>/dev/null
	@rm -rf dist 2>/dev/null
	@rm -rf src/aria2p.egg-info 2>/dev/null
	@rm -rf .coverage* 2>/dev/null
	@rm -rf .pytest_cache 2>/dev/null
	@rm -rf pip-wheel-metadata 2>/dev/null

test: check-ports clean-tests  ## Run the tests using pytest.
	poetry run pytest -n6 2>/dev/null
