import logging
import sys
from typing import IO

import click

from web_colors.web_colors import analyze_image, create_chart

logger = logging.getLogger(__name__)


@click.command()
@click.argument('input_image', type=click.File('rb'))
@click.argument('output_csv', type=click.File('wt'))
@click.argument('base_url', type=str, default='http://api.datawrapper.local')
@click.argument('auth_token', envvar='AUTH_TOKEN', type=str)
@click.option(
    '--verbose', '-v', is_flag=True, help='Enable debugging output',
)
def main(
    input_image: IO,
    output_csv: IO,
    base_url: str,
    auth_token: str,
    verbose: bool,
):
    """Analyze `input_image` and print results to `output_csv`."""
    if verbose:
        logging.basicConfig(
            stream=sys.stdout, level=logging.INFO, format='%(message)s'
        )
    data = analyze_image(input_image)
    data.to_csv(output_csv, index_label='color')
    create_chart(base_url, auth_token, title='Colors', data=data)
