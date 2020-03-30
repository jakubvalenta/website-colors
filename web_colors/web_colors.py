import json
from typing import IO, Tuple

import pandas as pd
import requests
from PIL import Image

RGB = Tuple[int, int, int]


def rgb2hex(rgb: RGB) -> str:
    r, g, b = rgb
    return f'#{r:02x}{g:02x}{b:02x}'


def analyze_image(f_in: IO, bg_color: RGB = (255, 255, 255)) -> pd.Series:
    im = Image.open(f_in)
    pixels = pd.Series(list(im.getdata()), name='frequency')
    fg_pixels = pixels[pixels != bg_color].apply(rgb2hex)
    fg_counts = fg_pixels.value_counts(normalize=True)
    fg_counts_large = fg_counts[fg_counts >= 0.01]
    return fg_counts_large


def create_chart(base_url: str, auth_token: str, title: str, data: pd.Series):
    props = {
        'title': title,
        'type': 'd3-pies',
        'metadata': {
            'visualize': {
                'custom-colors': {color: color for color in data.index},
                'group': {'num_slices': 50},
            },
        },
    }
    headers = {'Authorization': f'Bearer {auth_token}'}
    res = requests.post(
        base_url + '/v3/charts', headers=headers, data=json.dumps(props)
    )
    res.raise_for_status()
    chart_id = res.json()['id']
    csv = data.to_csv(index_label='color')
    res = requests.put(
        base_url + f'/charts/{chart_id}/data',
        headers={**headers, 'Content-Type': 'text/csv'},
        data=csv,
    )
    res.raise_for_status()
