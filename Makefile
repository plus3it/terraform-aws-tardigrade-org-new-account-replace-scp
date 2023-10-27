SHELL := /bin/bash
export PYTHONPATH := $(PYTHONPATH):./lambda/src
export TERRAFORM_PYTEST_DIR := $(PWD)/tests

include $(shell test -f .tardigrade-ci || curl -sSL -o .tardigrade-ci "https://raw.githubusercontent.com/plus3it/tardigrade-ci/master/bootstrap/Makefile.bootstrap"; echo .tardigrade-ci)

.PHONY: pytest/deps
pytest/deps:
	@ echo "[@] Installing dependencies used for unit and integration tests"
	@ python -m pip install \
		-r requirements/requirements_dev.txt \
		-r requirements/requirements_test.txt

.PHONY: python/deps
python/deps:
	@ echo "[$@] Installing lambda dependencies"
	@ python -m pip install -r lambda/src/requirements.txt
