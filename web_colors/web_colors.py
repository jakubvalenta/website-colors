import datetime
import json
import logging
from typing import IO, Tuple

import pandas as pd
import requests
from PIL import Image, UnidentifiedImageError

RGB = Tuple[int, int, int]

logger = logging.getLogger(__name__)


class ArchiveError(Exception):
    pass


def find_closest_snapshot_url(url: str, date: datetime.date) -> str:
    logger.info('Finding closest snaphot URL for %s %s', url, date)
    timestamp = date.strftime('%Y%m%d')
    api_url = f'https://web.archive.org/web/{timestamp}/{url}'
    res = requests.get(
        api_url, headers={'User-Agent': 'curl/7.69.1'}, allow_redirects=False
    )
    snapshot_url = res.headers.get('location')
    if not snapshot_url:
        raise ArchiveError('Failed to find snapshot URL')
    logger.info('Closes snapshot URL for %s %s is %s', url, date, snapshot_url)
    return snapshot_url


def rgb2hex(rgb: RGB) -> str:
    r, g, b = rgb
    return f'#{r:02x}{g:02x}{b:02x}'


def analyze_image(f_in: IO, bg_color: RGB = (255, 255, 255)) -> pd.Series:
    try:
        im = Image.open(f_in)
    except UnidentifiedImageError:
        logger.error('Failed to read image')
        return None
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
    logger.info('Creating chart %s', title)
    res = requests.post(
        base_url + '/v3/charts', headers=headers, data=json.dumps(props)
    )
    res.raise_for_status()
    chart_id = res.json()['id']
    logger.info('Created chart %s %s', title, chart_id)
    csv = data.to_csv(index_label='color')
    logger.info('Uploading data for chart %s %s', title, chart_id)
    res = requests.put(
        base_url + f'/charts/{chart_id}/data',
        headers={**headers, 'Content-Type': 'text/csv'},
        data=csv,
    )
    res.raise_for_status()
    logger.info('Uploaded data for chart %s %s', title, chart_id)
