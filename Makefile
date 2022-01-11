.PHONY: help
.DEFAULT_GOAL := help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install requirements
	pip install -r requirements.txt

fmt format: ## Run code formatters
	isort app tests main.py
	black app tests main.py

lint: ## Run code linters
	isort app tests main.py
	black app tests main.py
	isort --check app tests main.py
	black --check app tests main.py
	flake8 app tests main.py
	mypy app tests main.py
