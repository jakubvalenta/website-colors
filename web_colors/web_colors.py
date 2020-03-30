from pprint import pprint as pp
from typing import IO

import pandas as pd
from PIL import Image


def analyze_image(f_in: IO, f_out: IO):
    im = Image.open(f_in)
    pixels = pd.Series(list(im.getdata()), name='frequency')
    fg_pixels = pixels[pixels != (255, 255, 255)]
    fg_counts = fg_pixels.value_counts(normalize=True)
    fg_counts_large = fg_counts[fg_counts >= 0.01]
    fg_counts_large.to_csv(f_out, index_label='color')
