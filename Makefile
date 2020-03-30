_python_pkg = web_colors
_executable = web-colors
websites := google.com
data_dir := data
website_dirs := $(addprefix $(data_dir)/,$(websites))
date_start := 2018-01-01
date_end := 2020-01-01
every_months := 12
snapshot_dirs := $(wildcard $(data_dir)/*/*/)
url_paths := $(addsuffix url.txt,$(snapshot_dirs))
html_paths := $(addsuffix snapshot.html,$(snapshot_dirs))
screenshot_paths := $(addsuffix screenshot.png,$(snapshot_dirs))
csv_paths := $(addsuffix colors.csv,$(snapshot_dirs))
chart_paths := $(addsuffix /chart.csv,$(website_dirs))

.PHONY: find-snapshots screenshot analyze join chart setup setup-dev test lint tox reformat help

find-snapshots: $(website_dirs)  ## Find snapshot URLs for specified websites

$(website_dirs): | $(data_dir)
	"./$(_executable)" -v find-snapshots \
		--start "$(date_start)" --end "$(date_end)" \
		--every-months "$(every_months)" \
		"http://$$(basename "$@")/" "$@"

download: $(html_paths)  ## Download snapshots from found URLs

$(data_dir)/%/snapshot.html: $(data_dir)/%/url.txt
	url=$$(cat "$<"); \
	html_path=$$(dirname "$@")/snapshot.html; \
	"./$(_executable)" -v download "$$url" "$$html_path"

screenshot: $(screenshot_paths)  ## Make screenshots of downloaded snapshots

$(data_dir)/%/screenshot.png: $(data_dir)/%/snapshot.html
	screenshot_dir=$$(dirname "$@"); \
	cd "$$screenshot_dir" && \
	rm -f screenshot.png && \
	chromium --headless --disable-gpu --screenshot --window-size=1280,800 snapshot.html

analyze: $(csv_paths)  ## Analyze colors of the screenshots

$(data_dir)/%/colors.csv: $(data_dir)/%/screenshot.png
	if [[ $$(stat -c "%s" "$<") != "0" ]]; then \
		"./$(_executable)" -v analyze "$<" "$@"; \
	fi

join: $(chart_paths)  ## Join snapshot colors into one CSV for each website

$(data_dir)/%/chart.csv: $(csv_paths)
	chart_dir=$$(dirname "$@"); \
	"./$(_executable)" -v join "$$chart_dir" "$@"

chart: $(chart_paths)  ## Chart the joined snapshot colors CSVs
	for chart_path in $^; do \
		if [[ -f "$$chart_path" ]]; then \
			title=$$(basename "$$(dirname "$$chart_path")"); \
			"./$(_executable)" -v chart --title "$$title" "$$chart_path"; \
		fi; \
	done

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
