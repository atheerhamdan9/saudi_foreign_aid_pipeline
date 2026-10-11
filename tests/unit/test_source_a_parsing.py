import pytest

from pipeline.sources.source_a import read_source_a

ARABIC_HEADERS = [
    "عنوان المشروع",
    "حالة المشروع",
    "قطاع المشروع",
    "موقع المشروع",
    "مجموع التكاليف $",
    "الجهة المانحة للمشروع",
    "الدولة المستفيدة",
]


def test_reads_and_normalizes_arabic_columns(tmp_path):
    """Arabic source headers should become standardized English names."""
    csv_path = tmp_path / "source.csv"
    csv_path.write_text(
        ",".join(ARABIC_HEADERS)
        + "\nمشروع تجريبي,مكتمل,الصحة,اليمن,1000,الصندوق,اليمن\n",
        encoding="utf-8-sig",
    )

    records = read_source_a(csv_path)

    assert len(records) == 1
    assert records[0] == {
        "project_title": "مشروع تجريبي",
        "project_status": "مكتمل",
        "project_sector": "الصحة",
        "project_location": "اليمن",
        "total_cost_usd": "1000",
        "project_donor": "الصندوق",
        "beneficiary_country": "اليمن",
    }


def test_accepts_alternative_cost_column_name(tmp_path):
    """Common variations in the Arabic cost header should be accepted."""
    headers = ARABIC_HEADERS.copy()
    headers[4] = "إجمالي تكلفة المشروع"

    csv_path = tmp_path / "source.csv"
    csv_path.write_text(
        ",".join(headers)
        + "\nمشروع تجريبي,مكتمل,الصحة,اليمن,1000,الصندوق,اليمن\n",
        encoding="utf-8-sig",
    )

    records = read_source_a(csv_path)

    assert records[0]["total_cost_usd"] == "1000"


def test_rejects_missing_expected_column(tmp_path):
    """A CSV missing a required column should be rejected."""
    headers = ARABIC_HEADERS[:-1]
    csv_path = tmp_path / "source.csv"
    csv_path.write_text(
        ",".join(headers) + "\nمشروع تجريبي,مكتمل,الصحة,اليمن,1000,الصندوق\n",
        encoding="utf-8-sig",
    )

    with pytest.raises(ValueError, match="Missing expected columns"):
        read_source_a(csv_path)
