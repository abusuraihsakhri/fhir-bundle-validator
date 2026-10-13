"""Regression tests for CSV boolean parsing and batch urgency."""
import csv
import pytest
from cli import main, parse_csv_bool


@pytest.mark.parametrize(("value", "expected"), [
    ("false", False), ("False", False), ("0", False), ("", False),
    ("true", True), ("TRUE", True), ("1", True), ("yes", True),
])
def test_boolean_values(value, expected):
    assert parse_csv_bool(value) is expected


def test_bad_boolean():
    with pytest.raises(ValueError):
        parse_csv_bool("potentially")


def test_batch_flag_semantics(tmp_path):
    infile = tmp_path / "input.csv"
    outfile = tmp_path / "output.csv"
    with infile.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["task_id", "target_identifier", "primary_metric",
                                                     "secondary_metric", "status_descriptor", "is_critical_flag"])
        writer.writeheader()
        writer.writerow({"task_id": "A", "target_identifier": "A", "primary_metric": 1,
                         "secondary_metric": 1, "status_descriptor": "NOMINAL", "is_critical_flag": "false"})
        writer.writerow({"task_id": "B", "target_identifier": "B", "primary_metric": 1,
                         "secondary_metric": 1, "status_descriptor": "NOMINAL", "is_critical_flag": "true"})
    assert main(["batch", "-i", str(infile), "-o", str(outfile)]) == 0
    with outfile.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["overall_urgency"] == "ROUTINE"
    assert rows[1]["overall_urgency"] == "CRITICAL_STAT_PANIC"
