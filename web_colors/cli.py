import datetime
import logging
import sys
from pathlib import Path
from typing import IO

import click

from web_colors.analyze import analyze_image, read_analysis, write_analysis
from web_colors.archive import find_closest_snapshot_url, screenshot_snapshot
from web_colors.chart import create_chart, read_chart_data, write_chart_data
from web_colors.date_utils import date_range

logger = logging.getLogger(__name__)


@click.group()
@click.option(
    '--verbose', '-v', is_flag=True, help='Enable debugging output',
)
def cli(verbose: bool):
    if verbose:
        logging.basicConfig(
            stream=sys.stderr, level=logging.INFO, format='%(message)s'
        )


@cli.command()
@click.argument('url', type=str)
@click.argument('output_dir', type=click.Path(file_okay=False, dir_okay=True))
@click.option('--start', '-s', type=str, help='Find snapshots since')
@click.option('--end', '-e', type=str, help='Find snapshots until')
@click.option(
    '--every-months', '-m', type=int, help='Find a snapshot every # months',
)
def find_snapshot(
    url: str, output_dir: str, start: str, end: str, every_months: int,
):
    """Find archive URLs for `url` and save results to `output_dir`."""
    start_date = datetime.date.fromisoformat(start)
    end_date = datetime.date.fromisoformat(end)
    dates = date_range(start_date, end_date, every_months)
    for date in dates:
        snapshot_url = find_closest_snapshot_url(url, date)
        snapshot_dir = Path(output_dir) / date.isoformat()
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        snapshot_url_file = snapshot_dir / 'url.txt'
        snapshot_url_file.write_text(snapshot_url)


@cli.command()
@click.argument('url', type=str)
@click.argument('output_png', type=click.Path())
def screenshot(url: str, output_png: str):
    """Take a screenshot of `url` and write the PNG to `output_png`."""
    logger.info('Taking screenshot of snapshot %s > %s', url, output_png)
    screenshot_snapshot(url, output_png)


@cli.command()
@click.argument('input_image', type=click.File('rb'))
@click.argument('output_csv', type=click.File('wt'))
def analyze(input_image: IO, output_csv: IO):
    """Analyze `input_image` and print results to `output_csv`."""
    data = analyze_image(input_image)
    write_analysis(data, output_csv)


@cli.command()
@click.argument(
    'input_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.argument('output_csv', type=click.File('wt'))
def join(input_dir: str, output_csv: IO):
    """Join colors recursively found in directory `input_dir`."""
    csv_paths = Path(input_dir).glob('*/*.csv')
    if csv_paths:
        snapshot_dfs = (read_analysis(csv_path) for csv_path in csv_paths)
        write_chart_data(snapshot_dfs, output_csv)


@cli.command()
@click.argument('input_csv', type=click.File('rt'))
@click.option('--title', '-t', type=str, default='Colors')
@click.option('--base-url', type=str, default='http://api.datawrapper.local')
@click.option('--auth-token', envvar='AUTH_TOKEN', type=str)
def chart(input_csv: IO, title: str, base_url: str, auth_token: str):
    """Create chart from `input_csv`."""
    data = read_chart_data(input_csv)
    create_chart(base_url, auth_token, title, data)


if __name__ == '__main__':
    cli()
