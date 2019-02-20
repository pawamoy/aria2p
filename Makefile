.PHONY: help
.PHONY: test-py36
.PHONY: test-py37
.DEFAULT_GOAL := help

help: ## Print this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

readme: README.md  ## Regenerate README.md.
	poetry run ./scripts/gen-readme-data.py | \
		poetry run jinja2 --format=json scripts/templates/README.md > README.md

check: check-bandit check-black check-flake8 check-isort check-safety  ## Check it all!

check-black:  ## Check if code is formatted nicely using black.
	poetry run black --check src/ tests/

check-isort:  ## Check if imports are correctly ordered using isort.
	poetry run isort -c -rc src/ tests/

check-flake8:  ## Check for general warnings in code using flake8.
	poetry run flake8 src/ tests/

check-bandit:  ## Check for security warnings in code using bandit.
	poetry run bandit -r src/

check-safety:  ## Check for vulnerabilities in dependencies using safety.
	poetry run pip freeze 2>/dev/null | \
		grep -v aria2p | \
		poetry run safety check --stdin --full-report 2>/dev/null

run-black:  ## Lint the code using black.
	poetry run black src/ tests/

run-isort:  ## Sort the imports using isort.
	poetry run isort -y -rc src/ tests/

test:  ## Run the tests using pytest.
	poetry run pytest -n6 2>/dev/null
