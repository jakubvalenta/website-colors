import logging
import sys
from typing import IO

import click

from web_colors.web_colors import analyze_image

logger = logging.getLogger(__name__)


@click.command()
@click.argument('input_image', type=click.File('rb'))
@click.argument('output_csv', type=click.File('wt'))
@click.option(
    '--verbose', '-v', is_flag=True, help='Enable debugging output',
)
def main(input_image: IO, output_csv: IO, verbose: bool):
    """Analyze `input_image` and print results to `output_csv`."""
    if verbose:
        logging.basicConfig(
            stream=sys.stdout, level=logging.INFO, format='%(message)s'
        )
    analyze_image(input_image, output_csv)
