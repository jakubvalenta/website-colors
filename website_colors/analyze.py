import datetime
import logging
from typing import IO

import pandas as pd
from PIL import Image, ImageOps, UnidentifiedImageError

from website_colors.color_utils import color_8bit_to_float, rgb_to_hex

logger = logging.getLogger(__name__)


def analyze_image(
    path: str,
    date: datetime.date,
    posterize_bits: int = 4,
    min_frequency: float = 0.0001,
) -> pd.DataFrame:
    try:
        im = Image.open(path).convert(mode='RGB')
        im = ImageOps.posterize(im, posterize_bits)
        im_data = list(im.getdata())
    except UnidentifiedImageError:
        logger.error('Failed to read image, skipping')
        im_data = []
    pixels = pd.Series(im_data)
    pixels = pixels.apply(color_8bit_to_float)
    pixels = pixels.apply(rgb_to_hex)
    counts = pixels.value_counts(normalize=True)
    counts = counts[counts > min_frequency]
    counts = counts / counts.sum()
    df = pd.DataFrame(
        {'frequency': counts.values, 'date': date}, index=counts.index
    )
    return df


def read_analysis(f: IO) -> pd.DataFrame:
    logger.info('Reading analysis %s', f)
    return pd.read_csv(f)


def write_analysis(data: pd.Series, f: IO):
    logger.info('Writing analysis %s', f)
    data.to_csv(f, index_label='color')
