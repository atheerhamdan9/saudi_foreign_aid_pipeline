"""Configuration and local paths for the Saudi Foreign Aid pipeline."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
SOURCE_A_DIR = RAW_DATA_DIR / "source_a"

PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"

CONTRACTS_DIR = PROJECT_ROOT / "contracts"
