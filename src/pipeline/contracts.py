
from pathlib import Path
from typing import Any

import yaml


class ContractError(ValueError):
    """Raised when a data contract is invalid."""


def validate_contract(contract: Any) -> None:
    """Validate the basic structure of a data contract."""

    if not isinstance(contract, dict):
        raise ContractError("The contract must be a YAML mapping.")

    if type(contract.get("schema_version")) is not int:
        raise ContractError("schema_version must be an integer.")

    if not isinstance(contract.get("dataset"), str) or not contract["dataset"].strip():
        raise ContractError("dataset must be a non-empty string.")

    columns = contract.get("columns")
    if not isinstance(columns, list) or not columns:
        raise ContractError("columns must be a non-empty list.")

    allowed_types = {"string", "number", "integer", "date", "boolean"}
    column_names = set()

    for column in columns:
        if not isinstance(column, dict):
            raise ContractError("Each column must be a mapping.")

        for field in ("name", "type", "nullable"):
            if field not in column:
                raise ContractError(f"A column is missing the '{field}' field.")

        name = column["name"]
        if not isinstance(name, str) or not name.strip():
            raise ContractError("Each column name must be a non-empty string.")

        if name in column_names:
            raise ContractError(f"Duplicate column name: {name}")

        column_names.add(name)

        if column["type"] not in allowed_types:
            raise ContractError(
                f"Unsupported type for column '{name}': {column['type']}"
            )

        if not isinstance(column["nullable"], bool):
            raise ContractError(f"nullable must be true or false for '{name}'.")

        allowed_values = column.get("allowed_values")
        if allowed_values is not None and not isinstance(allowed_values, list):
            raise ContractError(f"allowed_values must be a list for '{name}'.")

    grain = contract.get("grain", {})
    if not isinstance(grain, dict):
        raise ContractError("grain must be a mapping.")

    primary_key = grain.get("primary_key")
    if primary_key is not None:
        if not isinstance(primary_key, list) or not primary_key:
            raise ContractError("primary_key must be a non-empty list or null.")

        unknown_columns = set(primary_key) - column_names
        if unknown_columns:
            raise ContractError(
                f"Primary key references unknown columns: {sorted(unknown_columns)}"
            )


def load_contract(path: str | Path) -> dict[str, Any]:
    """Load a YAML contract and validate its structure."""

    contract_path = Path(path)

    with contract_path.open("r", encoding="utf-8") as file:
        contract = yaml.safe_load(file)

    validate_contract(contract)
    return contract