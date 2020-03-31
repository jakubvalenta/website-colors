import json
import logging
from typing import IO, Iterable

import pandas as pd
import requests

from web_colors.color_utils import hex_to_h

logger = logging.getLogger(__name__)


def read_chart_data(f: IO) -> pd.DataFrame:
    return pd.read_csv(f, index_col='date')


def write_chart_data(snapshot_dfs: Iterable[pd.DataFrame], f: IO):
    df = pd.concat(snapshot_dfs)
    df['h'] = df['color'].apply(hex_to_h)
    df.sort_values(by='h', inplace=True)
    df['frequency'] = (df['frequency'] * 10000).round()
    df = df.pivot(index='date', columns='color', values='frequency').fillna(0)
    df.to_csv(f, index_label='date')


def create_chart(base_url: str, auth_token: str, title: str, data: pd.Series):
    props = {
        'title': title,
        'type': 'd3-area',
        'metadata': {
            'visualize': {
                'area-opacity': '1',
                'custom-colors': {color: color for color in data.columns},
                'interpolation': 'step',
                'label-colors': False,
                'labeling': 'off',
                'show-tooltips': False,
                'show-tooltips': False,
                'stack-to-100': True,
                'y-grid': 'off',
                'y-grid-format': '0%',
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
