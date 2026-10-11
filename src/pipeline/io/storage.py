"""Safe local file storage for the Saudi Foreign Aid pipeline."""

from pathlib import Path

from pipeline.config import RAW_DATA_DIR


def _resolve_key(key: str | Path, root: str | Path) -> Path:
    """Resolve a relative storage key and prevent paths outside the root."""
    relative_path = Path(key)

    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError("Storage key must be a safe relative path.")

    root_path = Path(root).resolve()
    target = (root_path / relative_path).resolve()

    if not target.is_relative_to(root_path):
        raise ValueError("Storage key must stay within the storage root.")

    return target


def put(
    key: str | Path,
    content: bytes,
    *,
    root: str | Path = RAW_DATA_DIR,
    overwrite: bool = False,
) -> Path:
    """Save bytes to local storage and return the destination path."""
    if not isinstance(content, bytes):
        raise TypeError("Storage content must be bytes.")

    target = _resolve_key(key, root)
    target.parent.mkdir(parents=True, exist_ok=True)

    if overwrite:
        target.write_bytes(content)
    else:
        # Use exclusive creation so an existing raw file is not replaced.
        with target.open("xb") as file:
            file.write(content)

    return target


def get(
    key: str | Path,
    *,
    root: str | Path = RAW_DATA_DIR,
) -> bytes:
    """Read bytes from local storage."""
    target = _resolve_key(key, root)

    if not target.is_file():
        raise FileNotFoundError(f"Stored file not found: {target}")

    return target.read_bytes()
