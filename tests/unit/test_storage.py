import pytest

from pipeline.io.storage import get, put


def test_put_and_get_bytes(tmp_path):
    content = b"raw source data"

    saved_path = put(
        "ingest_date=2026-10-11/sample.csv",
        content,
        root=tmp_path,
    )

    assert saved_path.is_file()
    assert get(
        "ingest_date=2026-10-11/sample.csv",
        root=tmp_path,
    ) == content


def test_put_does_not_overwrite_existing_file(tmp_path):
    put("sample.csv", b"original", root=tmp_path)

    with pytest.raises(FileExistsError):
        put("sample.csv", b"replacement", root=tmp_path)

    assert get("sample.csv", root=tmp_path) == b"original"


def test_storage_rejects_path_traversal(tmp_path):
    with pytest.raises(ValueError):
        put("../outside.csv", b"data", root=tmp_path)
