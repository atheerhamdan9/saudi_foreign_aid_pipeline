"""Command-line entry point for the Saudi Foreign Aid pipeline."""

from pipeline.config import CONTRACTS_DIR
from pipeline.contracts import load_contract


def main() -> int:
    """Validate the project's data contracts."""
    contract_files = [
        CONTRACTS_DIR / "source_a.yml",
        CONTRACTS_DIR / "fct_records_daily.yml",
    ]

    for path in contract_files:
        contract = load_contract(path)
        print(
            f"OK: {contract['dataset']} "
            f"({len(contract['columns'])} columns)"
        )

    print("Contract validation completed.")
    print(
        "Data transformation will be connected after the team "
        "agrees on the processing rules."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
