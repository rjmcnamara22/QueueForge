import csv
from dataclasses import dataclass
from io import StringIO

REQUIRED_COLUMNS = {"product", "quantity", "price"}


@dataclass
class ProcessingReport:
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_products: int
    missing_values: int
    invalid_numeric_values: int

def decode_csv(contents: bytes) -> str:
    encodings = (
        "utf-8",
        "utf-8-sig",
        "utf-16",
        "cp1252",
    )

    for encoding in encodings:
        try:
            return contents.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError(
        "CSV file must use a supported text encoding."
    )


def get_csv_headers(contents: bytes) -> list[str]:
    decoded = decode_csv(contents)
    reader = csv.reader(StringIO(decoded))

    try:
        return next(reader)
    except StopIteration:
        return []


def process_csv(contents: bytes) -> ProcessingReport:
    decoded = decode_csv(contents)
    reader = csv.DictReader(StringIO(decoded))

    if reader.fieldnames is None:
        raise ValueError("CSV file must contain a header row.")

    columns = set(reader.fieldnames)

    missing_columns = REQUIRED_COLUMNS - columns

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing_columns))}"
        )

    total_rows = 0
    valid_rows = 0
    invalid_rows = 0
    duplicate_products = 0
    missing_values = 0
    invalid_numeric_values = 0

    seen_products: set[str] = set()

    for row in reader:
        total_rows += 1
        row_is_valid = True

        product = row["product"].strip()
        quantity = row["quantity"].strip()
        price = row["price"].strip()

        if not product or not quantity or not price:
            missing_values += 1
            row_is_valid = False

        normalized_product = product.lower()

        if normalized_product:
            if normalized_product in seen_products:
                duplicate_products += 1
            else:
                seen_products.add(normalized_product)

        if quantity and price:
            try:
                quantity_value = int(quantity)
                price_value = float(price)

                if quantity_value < 0 or price_value < 0:
                    invalid_numeric_values += 1
                    row_is_valid = False

            except ValueError:
                invalid_numeric_values += 1
                row_is_valid = False

        if row_is_valid:
            valid_rows += 1
        else:
            invalid_rows += 1

    return ProcessingReport(
        total_rows=total_rows,
        valid_rows=valid_rows,
        invalid_rows=invalid_rows,
        duplicate_products=duplicate_products,
        missing_values=missing_values,
        invalid_numeric_values=invalid_numeric_values,
    )
