import csv
import datetime
import logging
import os
import sys
from pathlib import Path

import luigi

from website_colors.analyze import analyze_image, read_analysis, write_analysis
from website_colors.archive import (
    find_closest_snapshot_url, screenshot_snapshot,
)
from website_colors.chart import (
    create_chart, read_chart_data, write_chart_data,
)


class FindSnapshot(luigi.Task):
    data_path = luigi.Parameter()
    name = luigi.Parameter()
    url = luigi.Parameter()
    date = luigi.DateParameter()

    def output(self):
        return luigi.LocalTarget(
            Path(self.data_path)
            / self.name
            / self.date.isoformat()
            / 'url.txt'
        )

    def run(self):
        snapshot_url = find_closest_snapshot_url(self.url, self.date)
        with self.output().open('w') as f:
            print(snapshot_url, file=f)


class TakeScreenshot(luigi.Task):
    data_path = luigi.Parameter()
    name = luigi.Parameter()
    url = luigi.Parameter()
    date = luigi.DateParameter()

    def output(self):
        return luigi.LocalTarget(
            Path(self.data_path)
            / self.name
            / self.date.isoformat()
            / 'screenshot.png'
        )

    def requires(self):
        return FindSnapshot(
            data_path=self.data_path,
            name=self.name,
            url=self.url,
            date=self.date,
        )

    def run(self):
        with self.input().open('r') as f:
            url = f.readline()
        screenshot_snapshot(url, self.output().path)


class AnalyzeImage(luigi.Task):
    data_path = luigi.Parameter()
    name = luigi.Parameter()
    url = luigi.Parameter()
    date = luigi.DateParameter()

    def output(self):
        return luigi.LocalTarget(
            Path(self.data_path)
            / self.name
            / self.date.isoformat()
            / 'colors.csv'
        )

    def requires(self):
        return TakeScreenshot(
            data_path=self.data_path,
            name=self.name,
            url=self.url,
            date=self.date,
        )

    def run(self):
        data = analyze_image(self.input().path, self.date)
        with self.output().open('w') as f:
            write_analysis(data, f)


class CreateChartData(luigi.Task):
    data_path = luigi.Parameter()
    name = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(
            Path(self.data_path) / self.name / 'chart.csv'
        )

    def requires(self):
        input_path = Path(self.data_path) / self.name / 'input.csv'
        with input_path.open('r') as f:
            for row in csv.DictReader(f):
                url = row['url']
                date = datetime.date.fromisoformat(row['date'])
                yield AnalyzeImage(
                    data_path=self.data_path,
                    name=self.name,
                    url=url,
                    date=date,
                )

    def run(self):
        snapshot_dfs = []
        for input_ in self.input():
            with input_.open('r') as f:
                snapshot_df = read_analysis(f)
                snapshot_dfs.append(snapshot_df)
        with self.output().open('w') as f:
            write_chart_data(snapshot_dfs, f)


class CreateChart(luigi.Task):
    data_path = luigi.Parameter()
    name = luigi.Parameter()
    base_url = luigi.Parameter()
    auth_token = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(
            Path(self.data_path) / self.name / 'chart_id.txt'
        )

    def requires(self):
        return CreateChartData(data_path=self.data_path, name=self.name)

    def run(self):
        auth_token = self.auth_token or os.environ.get('AUTH_TOKEN')
        if not auth_token:
            raise ValueError('Auth token is not defined')
        with self.input().open('r') as f:
            data = read_chart_data(f)
        chart_id = create_chart(
            self.base_url, auth_token, title=self.name, data=data
        )
        with self.output().open('w') as f:
            print(chart_id, file=f)


class CreateCharts(luigi.Task):
    data_path = luigi.Parameter(default='./data')
    base_url = luigi.Parameter(default='https://api.datawrapper.de')
    auth_token = luigi.Parameter(default='')
    verbose = luigi.BoolParameter(default=False)

    def requires(self):
        for path in Path(self.data_path).glob('*/input.csv'):
            yield CreateChart(
                data_path=self.data_path,
                name=path.parent.name,
                base_url=self.base_url,
                auth_token=self.auth_token,
            )

    def run(self):
        if self.verbose:
            logging.basicConfig(
                stream=sys.stderr, level=logging.INFO, format='%(message)s'
            )


class CleanAnalysis(luigi.Task):
    data_path = luigi.Parameter(default='./data')

    def run(self):
        for input_path in Path(self.data_path).glob('*/input.csv'):
            website_path = input_path.parent
            with input_path.open('r') as f:
                for row in csv.DictReader(f):
                    date = row['date']
                    (website_path / date / 'colors.csv').unlink(
                        missing_ok=True
                    )
            (website_path / 'chart.csv').unlink(missing_ok=True)
            (website_path / 'chart_id.txt').unlink(missing_ok=True)
