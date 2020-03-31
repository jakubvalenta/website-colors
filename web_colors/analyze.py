import datetime
import logging
from pathlib import Path
from typing import IO

import pandas as pd
from PIL import Image, ImageOps, UnidentifiedImageError

from web_colors.color_utils import color_8bit_to_float, rgb_to_hex

logger = logging.getLogger(__name__)


def analyze_image(f_in: IO) -> pd.Series:
    try:
        im = Image.open(f_in).convert(mode='RGB')
    except UnidentifiedImageError:
        logger.error('Failed to read image, skipping')
        return None
    im = ImageOps.posterize(im, 3)
    pixels = pd.Series(list(im.getdata()), name='frequency')
    pixels = pixels.apply(color_8bit_to_float)
    pixels = pixels.apply(rgb_to_hex)
    counts = pixels.value_counts(normalize=True)
    counts = counts[counts < 0.8]
    counts = counts[counts > 0.0001]
    counts = counts / counts.sum()
    return counts


def read_analysis(csv_path: Path) -> pd.DataFrame:
    logger.info('Reading colors %s', csv_path)
    df = pd.read_csv(csv_path)
    df['date'] = datetime.date.fromisoformat(csv_path.parent.name)
    return df


def write_analysis(data: pd.Series, f: IO):
    if data is not None:
        data.to_csv(f, index_label='color')
