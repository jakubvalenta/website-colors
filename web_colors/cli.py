import datetime
import logging
import sys
from pathlib import Path
from typing import IO, Iterator

import click
import pandas as pd

from web_colors.web_colors import (
    analyze_image, create_chart, find_closest_snapshot_url,
)

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    pass


@click.group()
@click.option(
    '--verbose', '-v', is_flag=True, help='Enable debugging output',
)
def cli(verbose: bool):
    if verbose:
        logging.basicConfig(
            stream=sys.stderr, level=logging.INFO, format='%(message)s'
        )


def date_range(
    start_date: datetime.date, end_date: datetime.date, every_months: int,
) -> Iterator[datetime.date]:
    if start_date > end_date:
        raise ConfigError('Start date must be before end date')
    curr_date = start_date
    while curr_date <= end_date:
        yield curr_date
        if curr_date.month + every_months > 12:
            curr_date = datetime.date(
                curr_date.year + 1,
                curr_date.month + every_months - 12,
                curr_date.day,
            )
        else:
            curr_date = datetime.date(
                curr_date.year, curr_date.month + every_months, curr_date.day,
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
@click.argument('output_png', type=click.File('wb'))
def screenshot(url: str, output_png: IO):
    """Take a screenshot of a `url` and write it to `output_png`."""
    logger.info('Screenshot %s > %s', url, output_png.name)
    output_png.write(b'')


@cli.command()
@click.argument('input_image', type=click.File('rb'))
@click.argument('output_csv', type=click.File('wt'))
def analyze(input_image: IO, output_csv: IO):
    """Analyze `input_image` and print results to `output_csv`."""
    data = analyze_image(input_image)
    if data is not None:
        data.to_csv(output_csv, index_label='color')


def read_snapshot_df(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    date = datetime.date.fromisoformat(csv_path.parent.name)
    df['date'] = date
    return df.pivot(index='date', columns='color', values='frequency')


@cli.command()
@click.argument(
    'input_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.argument('output_csv', type=click.File('wt'))
def join(input_dir: str, output_csv: IO):
    """Join colors recursively found in directory `input_dir`."""
    snapshot_dfs = [
        read_snapshot_df(snapshot_csv)
        for snapshot_csv in Path(input_dir).glob('**/*.csv')
    ]
    if snapshot_dfs:
        df = pd.concat(snapshot_dfs)
        df.to_csv(output_csv, index_label='date')


@cli.command()
@click.argument('input_csv', type=click.File('rt'))
@click.option('--title', '-t', type=str, default='Colors')
@click.option('--base-url', type=str, default='http://api.datawrapper.local')
@click.option('--auth-token', envvar='AUTH_TOKEN', type=str)
def chart(input_csv: IO, title: str, base_url: str, auth_token: str):
    """Create chart from `input_csv`."""
    data = pd.read_csv(input_csv, index_col='date')
    create_chart(base_url, auth_token, title, data)


if __name__ == '__main__':
    cli()
