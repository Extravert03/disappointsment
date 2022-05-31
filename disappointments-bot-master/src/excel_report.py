import pathlib
from datetime import timedelta
from typing import Iterable

import xlsxwriter

import db
import settings


class DisappointmentsReport:

    def __init__(self, file_path: str | pathlib.Path):
        self._workbook = xlsxwriter.Workbook(file_path)
        self._worksheet = self._workbook.add_worksheet('All disappointments')

    def adjust_columns(self) -> None:
        columns = (
            ('A:A', 15),
            ('B:B', 10),
            ('C:C', 10),
            ('D:D', 100),
        )
        for column, width in columns:
            self._worksheet.set_column(column, width)

    def write_titles(self) -> None:
        titles = ('Created at', 'From user', 'To User', 'Reason')
        title_format = self._workbook.add_format({'bold': True})
        for column_no, title in enumerate(titles):
            self._worksheet.write_string(0, column_no, title, title_format)

    def write_disappointments(self, disappointments: Iterable[db.Disappointment]) -> None:
        date_format = self._workbook.add_format({'num_format': 'mmmm d yyyy'})
        for row, disappointment in enumerate(disappointments, start=1):
            created_at_by_bishkek_time = disappointment.created_at + timedelta(hours=6)
            self._worksheet.write_datetime(row, 0, created_at_by_bishkek_time, date_format)
            self._worksheet.write_string(row, 1, disappointment.from_user.name)
            self._worksheet.write_string(row, 2, disappointment.to_user.name)
            self._worksheet.write_string(row, 3, disappointment.reason)

    def close(self) -> None:
        self._workbook.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def generate_disappointments_report(disappointments: Iterable[db.Disappointment]) -> pathlib.Path:
    with DisappointmentsReport(settings.REPORT_FILE_PATH) as report:
        report.adjust_columns()
        report.write_titles()
        report.write_disappointments(disappointments)
    return settings.REPORT_FILE_PATH
