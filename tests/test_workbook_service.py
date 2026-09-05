"""Tests for WorkbookService — no Qt/GUI dependency."""
import json, os, shutil, sys, tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.services.workbook_service import WorkbookService

WB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "target.xlsm")


@pytest.fixture
def svc():
    return WorkbookService()


def test_parse_json_entries_array(svc):
    data = json.dumps([
        {"article_id": "A01", "expression": "test", "type": "Part for Whole", "occurrence": 1}
    ])
    entries, err = svc.parse_json(data)
    assert err is None
    assert len(entries) == 1


def test_parse_json_entries_object(svc):
    data = json.dumps({
        "entries": [
            {"article_id": "A01", "expression": "x", "type": "Other", "occurrence": 2}
        ]
    })
    entries, err = svc.parse_json(data)
    assert err is None
    assert len(entries) == 1


def test_parse_json_single_entry(svc):
    data = json.dumps(
        {"article_id": "A02", "expression": "y", "type": "Other", "occurrence": 1}
    )
    entries, err = svc.parse_json(data)
    assert err is None
    assert len(entries) == 1


def test_parse_json_invalid(svc):
    entries, err = svc.parse_json("not json {{{")
    assert err is not None
    assert entries == []


def test_parse_json_filters_summary(svc):
    data = json.dumps({
        "entries": [
            {"article_id": "A01", "expression": "x", "type": "Other", "occurrence": 1}
        ],
        "summary": {"total_unique_expressions": 1, "total_occurrences": 1}
    })
    entries, err = svc.parse_json(data)
    assert err is None
    assert len(entries) == 1


def test_validate_entries_missing_fields(svc):
    entries = [{"expression": "x", "type": "Other"}]  # missing article_id + occurrence
    warnings = svc.validate_entries(entries)
    assert any("article_id" in w or "occurrence" in w for w in warnings)


@pytest.mark.skipif(not os.path.exists(WB_PATH), reason="Real workbook not available")
def test_full_import_cycle(svc, tmp_path):
    wb_copy = tmp_path / "test.xlsm"
    shutil.copy(WB_PATH, wb_copy)
    info = svc.open(str(wb_copy))
    assert info["filename"] == "test.xlsm"
    assert "METONYMY CODING" in info["sheets"]

    entries = [
        {"article_id": "A01", "expression": "تێست", "type": "Institution for People",
         "occurrence": 2, "context": "ctx", "literal_referent": "lit",
         "metonymic_referent": "met", "interpretation": "interp"}
    ]
    result = svc.import_entries(entries)
    assert result["written"] == 1
    assert result["import_number"] == 1

    msg = svc.undo()
    assert msg is not None
    assert svc.import_count == 0
