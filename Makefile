.PHONY: clean clean-test clean-pyc clean-build help upgrade requirements
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 --max-line-length=120 src tests

test: ## run tests quickly with the default Python
	pytest

test-all: ## run tests on every Python version with tox
	tox

reformat: ## reformats all code files
	black --line-length 120 src tests

fixture_olx: ## creates ready for import course using tests fixture data
	tar -czvf olx_fixture.tar.gz tests/fixtures_data/studio_course_xml/*

fixture_cc: ## creates common cartridge file using tests fixture data
	rm -f cc_fixture.imscc; cd tests/fixtures_data/imscc_file/; zip -r ../../../cc_fixture.imscc *


coverage: ## check code coverage quickly with the default Python
	coverage run --source cc2olx -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

dist: clean ## builds source and wheel package
	python -m build
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	uv pip install .

upgrade: ## update uv.lock with the latest packages satisfying pyproject.toml
	uv run --with edx-lint edx_lint write_uv_constraints pyproject.toml
	uv lock --upgrade

requirements: ## install development environment requirements
	uv sync --locked --group dev
