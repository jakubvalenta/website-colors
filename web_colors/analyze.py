import datetime
import logging
from pathlib import Path
from typing import IO, Tuple

import pandas as pd
from PIL import Image, ImageOps, UnidentifiedImageError

logger = logging.getLogger(__name__)


def color_8bit_to_float(color_8bit: Tuple[int, ...]) -> Tuple[float, ...]:
    return tuple(x / 255 for x in color_8bit)


def rgb_to_hex(rgb: Tuple[float, float, float]) -> str:
    r, g, b = (round(x * 255) for x in rgb)
    return f'#{r:02x}{g:02x}{b:02x}'


def floor_to(v: float, step: float):
    return v // step * step


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
    date = datetime.date.fromisoformat(csv_path.parent.name)
    df['date'] = date
    df['frequency'] = (df['frequency'] * 100).round()
    return df.pivot(index='date', columns='color', values='frequency')


def write_analysis(data: pd.Series, f: IO):
    if data is not None:
        data.to_csv(f, index_label='color')
