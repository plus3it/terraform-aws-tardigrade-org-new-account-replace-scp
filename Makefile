SHELL := /bin/bash
export PYTHONPATH := $(PYTHONPATH):./lambda/src

include $(shell test -f .tardigrade-ci || curl -sSL -o .tardigrade-ci "https://raw.githubusercontent.com/plus3it/tardigrade-ci/master/bootstrap/Makefile.bootstrap"; echo .tardigrade-ci)

.PHONY: python/deps
python/deps:
	@ echo "[$@] Installing lambda dependencies"
	@ python -m pip install -r lambda/src/requirements.txt
