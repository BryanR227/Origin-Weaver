import csv
import sys
from pathlib import Path
from typing import Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_TEMPLATE_PATH = PROJECT_ROOT / "pdf" / "dnd_5e_character_sheet.csv"
DEFAULT_PDF_TEMPLATE_PATH = PROJECT_ROOT / "pdf" / "blank_sheet.pdf"


def _load_template():
    with CSV_TEMPLATE_PATH.open("r", newline="", encoding="utf-8") as template_file:
        reader = csv.DictReader(template_file)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if not fieldnames or not {"section", "field", "value", "format_hint"}.issubset(fieldnames):
        raise ValueError("The character sheet CSV template has an unexpected format.")

    field_keys = [f"{row['section']}||{row['field']}" for row in rows]
    if len(field_keys) != len(set(field_keys)):
        raise ValueError("The character sheet CSV template contains duplicate fields.")

    return fieldnames, rows


def get_character_field_keys():
    """Return the CSV field keys used to request structured character data."""
    _, rows = _load_template()
    return [f"{row['section']}||{row['field']}" for row in rows]


def write_character_csv(field_values: Mapping[str, str], output_path):
    """Write validated character values into a copy of the CSV template."""
    if not isinstance(field_values, Mapping):
        raise TypeError("Character field values must be a mapping.")

    fieldnames, rows = _load_template()
    allowed_keys = {f"{row['section']}||{row['field']}" for row in rows}
    unknown_keys = set(field_values) - allowed_keys
    if unknown_keys:
        raise ValueError(f"Unknown character sheet fields: {', '.join(sorted(unknown_keys))}")

    for key, value in field_values.items():
        if not isinstance(value, str):
            raise TypeError(f"Character sheet value for {key!r} must be a string.")

    values = {key: value.strip() for key, value in field_values.items()}
    for row in rows:
        key = f"{row['section']}||{row['field']}"
        row["value"] = values.get(key, "")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def generate_character_sheet(field_values: Mapping[str, str], pdf_template_path, output_dir):
    """Fill the PDF template from character values and return the finished sheet path."""
    pdf_template_path = Path(pdf_template_path).resolve()
    if not pdf_template_path.is_file():
        raise FileNotFoundError(f"Character sheet PDF template not found: {pdf_template_path}")

    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = write_character_csv(field_values, output_dir / "character.csv")

    project_root = str(PROJECT_ROOT)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from pdf.csv_to_char_sheet import main as convert_character_sheet

    convert_character_sheet(str(csv_path), str(pdf_template_path), str(output_dir))
    filled_sheet_path = output_dir / "filled_character_sheet.pdf"
    if not filled_sheet_path.is_file():
        raise RuntimeError("The PDF converter did not create the filled character sheet.")
    return filled_sheet_path