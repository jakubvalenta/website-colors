import datetime
import logging

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class ArchiveError(Exception):
    pass


def get_from_web_archive(url: str, *args, **kwargs) -> requests.Response:
    res = requests.get(
        url, *args, headers={'User-Agent': 'curl/7.69.1'}, **kwargs
    )
    res.raise_for_status()
    return res


def find_closest_snapshot_url(url: str, date: datetime.date) -> str:
    logger.info('Finding closest snaphot URL for %s %s', url, date)
    timestamp = date.strftime('%Y%m%d')
    api_url = f'https://web.archive.org/web/{timestamp}/{url}'
    res = get_from_web_archive(api_url, allow_redirects=False)
    snapshot_url = res.headers.get('location')
    if not snapshot_url:
        raise ArchiveError('Failed to find snapshot URL')
    logger.info('Closes snapshot URL for %s %s is %s', url, date, snapshot_url)
    return snapshot_url


def hide_wayback_machine_bar(
    driver: webdriver.Firefox, element_id: str = 'wm-ipp-base'
):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        driver.execute_script(
            'document.body.removeChild'
            f"(document.getElementById('{element_id}'))"
        )
        return True
    except TimeoutException:
        return False


def screenshot_snapshot(url: str, path: str):
    logger.info('Taking screenshot of snapshot %s > %s', url, path)
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    try:
        logger.info('Waiting for the Wayback Machine bar to appear')
        if hide_wayback_machine_bar(driver):
            driver.save_screenshot(path)
        else:
            driver.save_screenshot(path + '.error.png')
            logger.info(
                'The Wayback Machine bar didn\'t appear, '
                'saving and empty screenshot file'
            )
            with open(path, 'w') as f:
                f.write('')
    finally:
        driver.quit()
