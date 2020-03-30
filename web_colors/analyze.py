import datetime
import logging
from pathlib import Path
from typing import IO, Tuple

import pandas as pd
from PIL import Image, UnidentifiedImageError

RGB = Tuple[int, int, int]

logger = logging.getLogger(__name__)


def rgb2hex(rgb: RGB) -> str:
    r, g, b = rgb
    return f'#{r:02x}{g:02x}{b:02x}'


def analyze_image(f_in: IO, bg_color: RGB = (255, 255, 255)) -> pd.Series:
    try:
        im = Image.open(f_in)
    except UnidentifiedImageError:
        logger.error('Failed to read image, skipping')
        return None
    im_rgb = im.convert(mode='RGB')
    pixels = pd.Series(list(im_rgb.getdata()), name='frequency')
    fg_pixels = pixels[pixels != bg_color].apply(rgb2hex)
    fg_counts = fg_pixels.value_counts(normalize=True)
    fg_counts_large = fg_counts[fg_counts >= 0.01]
    return fg_counts_large


def read_analysis(csv_path: Path) -> pd.DataFrame:
    logger.info('Reading colors %s', csv_path)
    df = pd.read_csv(csv_path)
    date = datetime.date.fromisoformat(csv_path.parent.name)
    df['date'] = date
    df['frequency'] = (df['frequency'] * 100).round()
    return df.pivot(index='date', columns='color', values='frequency')


def write_analysis(data: pd.Series, f: IO):
    if data is not None:
        data.to_csv(f, index_label='color')
