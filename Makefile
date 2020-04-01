_python_pkg = web_colors
_executable = web-colors
_executable_clean = web-colors-clean
data_dir := data
workers := 2
args := --verbose --workers $(workers)

.PHONY: run clean clean-analysis clean-joined setup setup-dev test lint tox reformat help

run:  ## Run the pipeline
	"./$(_executable)" $(args) \
		--title Google \
		--url http://www.google.com/ \
		--date-interval 2001-02-01-2020-02-01 \
		--every-months 6
	"./$(_executable)" $(args) \
		--title Wikipedia \
		--url http://en.wikipedia.org/wiki/Main_Page \
		--date-interval 2001-02-01-2020-02-01 \
		--every-months 12
	"./$(_executable)" $(args) \
		--title Amazon \
		--url http://www.amazon.com/ \
		--date-interval 2001-02-01-2020-02-01 \
		--every-months 12
	"./$(_executable)" $(args) \
		--title BBC \
		--url http://www.bbc.com/news \
		--date-interval 2001-02-01-2020-02-01 \
		--every-months 12
	# "./$(_executable)" $(args) \
	#	--title eBay \
	#	--url http://www.ebay.com/ \
	#	--date-interval 2001-02-01-2020-02-01 \
	#	--every-months 12
	# "./$(_executable)" $(args) \
	#	--title Yahoo Mail \
	#	--url http://mail.yahoo.com/ \
	#	--date-interval 2001-02-01-2020-02-01 \
	#	--every-months 12

clean:  ## Remove all intermediate files except URLs and screenshots
	"./$(_executable_clean)" \
		--url http://www.google.com/ \
		--date-interval 2001-02-01-2020-02-01 \
		--every-months 6
	"./$(_executable_clean)" \
		--url http://en.wikipedia.org/wiki/Main_Page \
		--date-interval 2001-02-01-2020-02-01 \
		--every-months 12
	"./$(_executable_clean)" \
		--url http://www.amazon.com/ \
		--date-interval 2001-02-01-2020-02-01 \
		--every-months 12
	"./$(_executable_clean)" \
		--url http://www.bbc.com/news \
		--date-interval 2001-02-01-2020-02-01 \
		--every-months 12

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
