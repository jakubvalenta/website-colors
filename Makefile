_python_pkg = web_colors
_executable = web-colors
data_dir := data

.PHONY: run clean clean-analysis clean-joined setup setup-dev test lint tox reformat help

run:
	"./$(_executable)" \
		--verbose \
		--website google.com \
		--date-interval 2001-02-01-2020-02-01 \
		--every-months 6

clean: | clean-analysis clean-joined  ## Remove all intermediate files

clean-analysis:  ## Remove all colors.csv files
	-rm -I $(data_dir)/*/*/colors.csv

clean-joined:  ## Remove all chart.csv files
	-rm -I $(data_dir)/*/chart.csv

setup:  ## Create Pipenv virtual environment and install dependencies.
	pipenv --three --site-packages
	pipenv install

setup-dev:  ## Install development dependencies
	pipenv install --dev

test:  ## Run unit tests
	pipenv run python -m unittest

lint:  ## Run linting
	pipenv run flake8 $(_python_pkg)
	pipenv run mypy $(_python_pkg) --ignore-missing-imports
	pipenv run isort -c -rc $(_python_pkg)

tox:  ## Test with tox
	tox -r

reformat:  ## Reformat Python code using Black
	black -l 79 --skip-string-normalization $(_python_pkg)

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
