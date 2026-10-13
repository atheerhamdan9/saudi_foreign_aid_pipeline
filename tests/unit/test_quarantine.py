"""Unit tests for source record quarantine."""

import pandas as pd

from pipeline.quarantine import split_valid_and_quarantined


def sample_record(**overrides):
    record = {
        "record": 1,
        "project_title": "Hospital Construction",
        "project_status": "Completed",
        "project_sector": "Health",
        "project_location": "Riyadh",
        "total_cost_usd": "1000",
        "project_donor": "Saudi Arabia",
        "beneficiary_country": "Yemen",
        "snapshot_month": "2026-03",
    }
    record.update(overrides)
    return record


def test_valid_record():
    raw = pd.DataFrame([sample_record()])

    valid, quarantined = split_valid_and_quarantined(raw)

    assert len(valid) == 1
    assert quarantined.empty


def test_invalid_cost_is_quarantined():
    raw = pd.DataFrame([
        sample_record(total_cost_usd="invalid")
    ])

    valid, quarantined = split_valid_and_quarantined(raw)

    assert valid.empty
    assert len(quarantined) == 1
    assert "total_cost_usd" in quarantined.iloc[0]["rejection_reason"]
    assert quarantined.iloc[0]["total_cost_usd"] == "invalid"


def test_blank_text_is_quarantined():
    raw = pd.DataFrame([
        sample_record(project_title="   ")
    ])

    valid, quarantined = split_valid_and_quarantined(raw)

    assert valid.empty
    assert len(quarantined) == 1
    assert "project_title" in quarantined.iloc[0]["rejection_reason"]


def test_mixed_records():
    raw = pd.DataFrame([
        sample_record(record=1),
        sample_record(record=2, total_cost_usd="invalid"),
        sample_record(record=3, project_sector=""),
    ])

    valid, quarantined = split_valid_and_quarantined(raw)

    assert len(valid) == 1
    assert len(quarantined) == 2
    assert set(quarantined["record"]) == {2, 3}
    assert quarantined["quarantined_at"].notna().all()

def test_invalid_record_number_is_quarantined():
    raw = pd.DataFrame([
        sample_record(record=0),
        sample_record(record=2),
    ])

    valid, quarantined = split_valid_and_quarantined(raw)

    assert len(valid) == 1
    assert len(quarantined) == 1
    assert quarantined.iloc[0]["record"] == 0
    assert "record" in quarantined.iloc[0]["rejection_reason"]

def test_duplicate_record_numbers_are_quarantined():
    raw = pd.DataFrame([
        sample_record(record=1),
        sample_record(record=1, project_title="School Project"),
        sample_record(record=2),
    ])

    valid, quarantined = split_valid_and_quarantined(raw)

    assert len(valid) == 2
    assert len(quarantined) == 1
    assert quarantined.iloc[0]["project_title"] == "School Project"
    assert "record" in quarantined.iloc[0]["rejection_reason"]
