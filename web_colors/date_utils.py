import datetime
from typing import Iterator


def date_range(
    start_date: datetime.date, end_date: datetime.date, every_months: int,
) -> Iterator[datetime.date]:
    if start_date > end_date:
        raise ValueError('Start date must be before end date')
    curr_date = start_date
    while curr_date <= end_date:
        yield curr_date
        if curr_date.month + every_months > 12:
            curr_date = datetime.date(
                curr_date.year + 1,
                curr_date.month + every_months - 12,
                curr_date.day,
            )
        else:
            curr_date = datetime.date(
                curr_date.year, curr_date.month + every_months, curr_date.day,
            )
