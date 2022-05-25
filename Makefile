TEST_PATH=./tests

.DEFAULT_GOAL := help

.PHONY: help clean-pyc build clean-build venv dependencies test-dependencies update-dependencies clean-venv test test-reports clean-test check-codestyle check-docstyle check-security check-dependencies check-codemetrics check-pytype check-annotations

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean-pyc: ## Remove python artifacts.
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

build: ## build a package
	python setup.py sdist bdist_wheel

clean-build:  ## clean build artifacts
	rm -rf build
	rm -rf dist
	rm -rf vendors
	rm -rf rest_model_service.egg-info

venv: ## create virtual environment
	python3.9 -m venv venv

dependencies: ## install dependencies from requirements.txt
	python -m pip install --upgrade pip
	python -m pip install --upgrade setuptools
	python -m pip install --upgrade wheel
	pip install -r requirements.txt

test-dependencies: ## install dependencies from test_requirements.txt
	pip install -r test_requirements.txt

update-dependencies:  ## Update dependency versions
	pip-compile requirements.in > requirements.txt
	pip-compile test_requirements.in > test_requirements.txt

clean-venv: ## remove all packages from virtual environment
	pip freeze | grep -v "^-e" | xargs pip uninstall -y

test: clean-pyc ## Run unit test suite.
	pytest --verbose --color=yes $(TEST_PATH)

test-reports: clean-pyc clean-test ## Run unit test suite with reporting
	mkdir -p reports
	mkdir ./reports/unit_tests
	mkdir ./reports/coverage
	mkdir ./reports/badge
	python -m coverage run --source rest_model_service -m pytest --verbose --color=yes --html=./reports/unit_tests/report.html --junitxml=./reports/unit_tests/report.xml $(TEST_PATH)
	coverage html -d ./reports/coverage
	coverage-badge -o ./reports/badge/coverage.svg

clean-test:	## Remove test artifacts
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf reports
	rm -rf .pytype

check-codestyle:  ## Check the style of the code against PEP8
	pycodestyle rest_model_service --max-line-length=120

check-docstyle:  ## Check the style of the docstrings against PEP257
	pydocstyle rest_model_service

check-security:  ## Check for common security vulnerabilities
	bandit -r rest_model_service

check-dependencies:  ## Check for security vulnerabilities in dependencies
	safety check -r requirements.txt

check-codemetrics:  ## Calculate code metrics of the package
	radon cc rest_model_service

check-pytype:  ## Perform static code analysis
	pytype rest_model_service

check-annotations: ## Check for type annotations coverage
	flake8 rest_model_service --max-line-length=120
