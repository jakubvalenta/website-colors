_python_pkg := website_colors
_executable := website-colors
_executable_clean := website-colors-clean

.PHONY: run
run:  ## Run the pipeline
	"./$(_executable)" --verbose $(args) --workers 2

.PHONY: clean
clean:  ## Remove all intermediate files except URLs and screenshots
	"./$(_executable_clean)" $(args)

.PHONY: setup
setup:  ## Create Pipenv virtual environment and install dependencies.
	pipenv --three --site-packages
	pipenv install

.PHONY: setup-dev
setup-dev:  ## Install development dependencies
	pipenv install --dev

.PHONY: test
test:  ## Run unit tests
	pipenv run python -m unittest

.PHONY: lint
lint:  ## Run linting
	pipenv run flake8 $(_python_pkg)
	pipenv run mypy $(_python_pkg) --ignore-missing-imports
	pipenv run isort -c $(_python_pkg)

.PHONY: tox
tox:  ## Test with tox
	tox -r

.PHONY: reformat
reformat:  ## Reformat Python code using Black
	black -l 79 --skip-string-normalization $(_python_pkg)
	pipenv run isort $(_python_pkg)

.PHONY: python-shell
python-shell:  ## Run Python shell with all dependencies installed
	pipenv run ipython --no-banner --no-confirm-exit

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
