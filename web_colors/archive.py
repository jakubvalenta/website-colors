import datetime
import logging
from typing import IO

import requests
from bs4 import BeautifulSoup

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


def download_snapshot(url: str, f: IO):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    soup.find(id='wm-ipp-base')['style'] = 'display: none'
    print(soup, file=f)
