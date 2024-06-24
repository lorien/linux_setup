.PHONY: init venv deps dirs clean release mypy pylint ruff check build eradicate render

.DEFAULT_GOAL := check
FILES_CHECK_MYPY = render render_html.py
FILES_CHECK_ALL = $(FILES_CHECK_MYPY)
PYTHON_VER="python3.12"

init: venv deps dirs

venv:
	if which $(PYTHON_VER); then \
		PYTHON_BINARY=$(PYTHON_VER); \
	else \
		PYTHON_BINARY=var/bin/$(PYTHON_VER); \
	fi; \
	uv venv --python $$PYTHON_BINARY .venv

deps:
	#curl -sS https://bootstrap.pypa.io/get-pip.py | .env/bin/python3 # a fix for manually built python
	#.env/bin/python -m pip install -U setuptools wheel # a fix for manually built python
	#.env/bin/pip install -r requirements_dev.txt
	uv pip install -U setuptools wheel # a fix for manually built python
	uv pip install -r requirements_dev.txt
	

dirs:
	if [ ! -e var/run ]; then mkdir -p var/run; fi
	if [ ! -e var/log ]; then mkdir -p var/log; fi

clean:
	find -name '*.pyc' -delete
	find -name '*.swp' -delete
	find -name '__pycache__' -delete

mypy:
	mypy --strict $(FILES_CHECK_MYPY)

pylint:
	pylint -j0 $(FILES_CHECK_ALL)

ruff:
	ruff check $(FILES_CHECK_ALL)

check: ruff mypy pylint

build:
	rm -rf *.egg-info
	rm -rf dist/*
	python -m build --sdist

render:
	python render_html.py > html/install.html
