from pathlib import Path

import pytest

from pipeline.contracts import (
    ContractError,
    load_contract,
    validate_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_source_contract_loads():
    """The source contract should contain the seven expected columns."""
    path = PROJECT_ROOT / "contracts" / "source_a.yml"
    contract = load_contract(path)

    assert contract["dataset"] == "source_a"
    assert len(contract["columns"]) == 7

    column_names = {column["name"] for column in contract["columns"]}

    assert column_names == {
        "project_title",
        "project_status",
        "project_sector",
        "project_location",
        "total_cost_usd",
        "project_donor",
        "beneficiary_country",
    }


def test_analytical_contract_loads():
    """The analytical contract should describe five output columns."""
    path = PROJECT_ROOT / "contracts" / "fct_records_daily.yml"
    contract = load_contract(path)

    assert contract["dataset"] == "fct_records_by_snapshot"
    assert len(contract["columns"]) == 5


def test_contract_rejects_missing_schema_version():
    """A contract without a schema version should be rejected."""
    contract = {
        "dataset": "example",
        "columns": [
            {"name": "value", "type": "string", "nullable": False}
        ],
    }

    with pytest.raises(ContractError, match="schema_version"):
        validate_contract(contract)


def test_contract_rejects_duplicate_column_names():
    """Column names must be unique within a contract."""
    contract = {
        "schema_version": 1,
        "dataset": "example",
        "columns": [
            {"name": "value", "type": "string", "nullable": False},
            {"name": "value", "type": "number", "nullable": False},
        ],
    }

    with pytest.raises(ContractError, match="Duplicate column name"):
        validate_contract(contract)


def test_contract_rejects_unknown_primary_key_column():
    """A primary key must reference columns that exist."""
    contract = {
        "schema_version": 1,
        "dataset": "example",
        "columns": [
            {"name": "value", "type": "string", "nullable": False}
        ],
        "grain": {"primary_key": ["missing_column"]},
    }

    with pytest.raises(ContractError, match="unknown columns"):
        validate_contract(contract)
