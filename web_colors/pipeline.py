import logging
import os
import re
import sys
from pathlib import Path

import luigi

from web_colors.analyze import analyze_image, read_analysis, write_analysis
from web_colors.archive import find_closest_snapshot_url, screenshot_snapshot
from web_colors.chart import create_chart, read_chart_data, write_chart_data
from web_colors.date_utils import date_range

DATA_PATH = 'data'


class URLParameterMixin:
    url = luigi.Parameter()

    @property
    def dirname(self) -> str:
        return re.sub(r'[^A-Za-z0-9_\-\.]', '_', self.url)


class FindSnapshot(URLParameterMixin, luigi.Task):
    date = luigi.DateParameter()

    def output(self):
        return luigi.LocalTarget(
            Path(DATA_PATH) / self.dirname / self.date.isoformat() / 'url.txt'
        )

    def run(self):
        snapshot_url = find_closest_snapshot_url(self.url, self.date)
        with self.output().open('w') as f:
            print(snapshot_url, file=f)


class TakeScreenshot(URLParameterMixin, luigi.Task):
    date = luigi.DateParameter()

    def output(self):
        return luigi.LocalTarget(
            Path(DATA_PATH)
            / self.dirname
            / self.date.isoformat()
            / 'screenshot.png'
        )

    def requires(self):
        return FindSnapshot(url=self.url, date=self.date)

    def run(self):
        with self.input().open('r') as f:
            url = f.readline()
        screenshot_snapshot(url, self.output().path)


class AnalyzeImage(URLParameterMixin, luigi.Task):
    date = luigi.DateParameter()

    def output(self):
        return luigi.LocalTarget(
            Path(DATA_PATH)
            / self.dirname
            / self.date.isoformat()
            / 'colors.csv'
        )

    def requires(self):
        return TakeScreenshot(url=self.url, date=self.date)

    def run(self):
        data = analyze_image(self.input().path, self.date)
        with self.output().open('w') as f:
            write_analysis(data, f)


class CreateChartData(URLParameterMixin, luigi.Task):
    date_interval = luigi.DateIntervalParameter()
    every_months = luigi.IntParameter()

    def output(self):
        return luigi.LocalTarget(Path(DATA_PATH) / self.dirname / 'chart.csv')

    def requires(self):
        dates = date_range(
            self.date_interval.date_a,
            self.date_interval.date_b,
            self.every_months,
        )
        for date in dates:
            yield AnalyzeImage(url=self.url, date=date)

    def run(self):
        snapshot_dfs = []
        for input_ in self.input():
            with input_.open('r') as f:
                snapshot_df = read_analysis(f)
                snapshot_dfs.append(snapshot_df)
        with self.output().open('w') as f:
            write_chart_data(snapshot_dfs, f)


class CreateChart(URLParameterMixin, luigi.Task):
    title = luigi.Parameter()
    date_interval = luigi.DateIntervalParameter()
    every_months = luigi.IntParameter()
    base_url = luigi.Parameter(default='http://api.datawrapper.local')
    auth_token = luigi.Parameter(default='')
    verbose = luigi.BoolParameter(default=False)

    def requires(self):
        return CreateChartData(
            url=self.url,
            date_interval=self.date_interval,
            every_months=self.every_months,
        )

    def run(self):
        if self.verbose:
            logging.basicConfig(
                stream=sys.stderr, level=logging.INFO, format='%(message)s'
            )
        auth_token = self.auth_token or os.environ.get('AUTH_TOKEN')
        if not auth_token:
            raise ValueError('Auth token is not defined')
        with self.input().open('r') as f:
            data = read_chart_data(f)
        create_chart(self.base_url, auth_token, self.title, data)


class CleanAnalysis(URLParameterMixin, luigi.Task):
    date_interval = luigi.DateIntervalParameter()
    every_months = luigi.IntParameter()

    def run(self):
        dates = date_range(
            self.date_interval.date_a,
            self.date_interval.date_b,
            self.every_months,
        )
        website_path = Path(DATA_PATH) / self.dirname
        for date in dates:
            (website_path / date.isoformat() / 'colors.csv').unlink(
                missing_ok=True
            )
        (website_path / 'chart.csv').unlink(missing_ok=True)
