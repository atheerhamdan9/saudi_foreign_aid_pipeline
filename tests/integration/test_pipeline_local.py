import csv
from pathlib import Path

from pipeline.cli import run_local_pipeline

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "source_a_sample.csv"
)


def test_local_pipeline_reads_transforms_and_writes_output(tmp_path):
    """The local pipeline should transform a CSV and write the results."""
    output_path = tmp_path / "processed" / "aid_projects.csv"

    record_count = run_local_pipeline(
        input_path=FIXTURE_PATH,
        output_path=output_path,
    )

    assert output_path.exists()
    assert record_count == 2

    with output_path.open("r", encoding="utf-8", newline="") as file:
        records = list(csv.DictReader(file))

    assert len(records) == 2
    assert records[0]["project_title"] == "مشروع صحة"
    assert records[0]["total_cost_usd"] == "1000"

    expected_columns = {
        "project_title",
        "project_status",
        "project_sector",
        "project_location",
        "total_cost_usd",
        "project_donor",
        "beneficiary_country",
    }
    assert set(records[0]) == expected_columns
