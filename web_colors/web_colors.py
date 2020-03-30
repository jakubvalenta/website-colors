from typing import IO, Tuple

import pandas as pd
from PIL import Image

RGB = Tuple[int, int, int]


def rgb2hex(rgb: RGB) -> str:
    r, g, b = rgb
    return f'#{r:02x}{g:02x}{b:02x}'


def analyze_image(f_in: IO, f_out: IO, bg_color: RGB = (255, 255, 255)):
    im = Image.open(f_in)
    pixels = pd.Series(list(im.getdata()), name='frequency')
    fg_pixels = pixels[pixels != bg_color].apply(rgb2hex)
    fg_counts = fg_pixels.value_counts(normalize=True)
    fg_counts_large = fg_counts[fg_counts >= 0.01]
    fg_counts_large.to_csv(f_out, index_label='color')


def create_chart(data: pd.Series):
    props = {
        'visualize': {
            'custom_colors': [[color, color] for color in data.index]
        }
    }
