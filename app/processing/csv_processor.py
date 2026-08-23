import csv
from io import StringIO


def get_csv_headers(contents: bytes) -> list[str]:
    decoded = contents.decode("utf-8")
    reader = csv.reader(StringIO(decoded))

    try:
        return next(reader)
    except StopIteration:
        return []