
import pytest

from pipeline.transform import transform_records


def sample_record(**overrides):
    record = {
        "project_title": " Health Project ",
        "project_status": "Completed",
        "project_sector": "Health",
        "project_location": "Yemen",
        "total_cost_usd": "1,000",
        "project_donor": "Saudi Fund",
        "beneficiary_country": "Yemen",
    }
    record.update(overrides)
    return record


def test_transform_trims_text_and_converts_cost():
    records = [sample_record()]

    result = transform_records(records)

    assert len(result) == 1
    assert result[0]["project_title"] == "Health Project"
    assert result[0]["total_cost_usd"] == 1000


def test_transform_removes_exact_duplicates():
    records = [
        sample_record(),
        sample_record(),
    ]

    result = transform_records(records)

    assert len(result) == 1


def test_transform_keeps_records_with_different_values():
    records = [
        sample_record(project_title="Health Project"),
        sample_record(project_title="Education Project"),
    ]

    result = transform_records(records)

    assert len(result) == 2


def test_transform_rejects_invalid_cost():
    records = [sample_record(total_cost_usd="not available")]

    with pytest.raises(ValueError, match="total_cost_usd"):
        transform_records(records)