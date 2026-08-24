from app.processing.csv_processor import process_csv


def test_process_csv_generates_report() -> None:
    contents = (
        b"product,quantity,price\n"
        b"Miller Lite,48,3.50\n"
        b"Bud Light,36,3.25\n"
        b"Miller Lite,12,3.50\n"
        b"Corona,,4.00\n"
        b"Coors Light,24,-2.00\n"
    )

    report = process_csv(contents)

    assert report.total_rows == 5
    assert report.valid_rows == 3
    assert report.invalid_rows == 2
    assert report.duplicate_products == 1
    assert report.missing_values == 1
    assert report.invalid_numeric_values == 1

def test_process_csv_rejects_missing_required_columns() -> None:
    contents = (
        b"product,quantity\n"
        b"Miller Lite,48\n"
    )

    try:
        process_csv(contents)
    except ValueError as error:
        assert str(error) == "Missing required columns: price"
    else:
        raise AssertionError("Expected ValueError")