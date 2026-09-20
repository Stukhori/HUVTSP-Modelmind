from io import BytesIO
from pathlib import Path
import tempfile

import openpyxl
import pytest

import app as modelmind


@pytest.fixture
def client(monkeypatch):
    with tempfile.TemporaryDirectory() as folder:
        monkeypatch.setitem(modelmind.app.config, "UPLOAD_FOLDER", folder)
        monkeypatch.setitem(modelmind.app.config, "TESTING", True)
        monkeypatch.setattr(modelmind, "call_gemini_api", lambda prompt: "<p>Test answer</p>")
        yield modelmind.app.test_client()


def workbook_bytes():
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Sales"
    sheet.append(["Month", "Revenue"])
    sheet.append(["January", 120])
    content = BytesIO()
    workbook.save(content)
    content.seek(0)
    return content


def test_only_xlsx_is_advertised_and_accepted(client):
    assert modelmind.allowed_file("sample.xlsx")
    assert not modelmind.allowed_file("sample.xls")
    assert not modelmind.allowed_file("sample.csv")
    response = client.post(
        "/upload",
        data={"excel_file": (workbook_bytes(), "sample.xlsx"), "user_question": "What is the revenue?"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"Test answer" in response.data


def test_xls_receives_actionable_error(client):
    response = client.post(
        "/upload",
        data={"excel_file": (BytesIO(b"not an xlsx"), "sample.xls"), "user_question": "Summarize"},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"Please use an .xlsx workbook" in response.data


def test_home_preserves_analysis_until_explicit_reset(client):
    response = client.post(
        "/upload",
        data={"excel_file": (workbook_bytes(), "sample.xlsx"), "user_question": "Summarize"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"Continue analysis" in client.get("/").data
    assert b"Test answer" in client.get("/result").data
    with client.session_transaction() as state:
        uploaded = Path(state["file_data"]["file_path"])
    assert uploaded.exists()
    response = client.post("/new_analysis", follow_redirects=True)
    assert b"Ready for a new workbook" in response.data
    assert not uploaded.exists()
    with client.session_transaction() as state:
        assert "file_data" not in state
        assert "qa_history" not in state


def test_switching_sheet_never_presents_a_fabricated_model_answer(client):
    workbook = openpyxl.Workbook()
    workbook.active.title = "Sales"
    workbook.active.append(["Revenue"])
    workbook.active.append([120])
    workbook.create_sheet("Costs").append(["Cost"])
    content = BytesIO()
    workbook.save(content)
    content.seek(0)
    client.post(
        "/upload",
        data={"excel_file": (content, "sample.xlsx"), "user_question": "Summarize"},
        content_type="multipart/form-data",
    )
    switched = client.post("/switch_sheet", data={"sheet_name": "Costs"})
    assert b"Switching sheets does not generate a new answer" in switched.data
    assert b"Test answer" not in switched.data
    refreshed = client.get("/result")
    assert b"Switching sheets does not generate a new answer" in refreshed.data
    follow_up = client.post("/ask_another", data={"user_question": "What is in this sheet?"})
    assert b"Test answer" in follow_up.data


def test_explicit_scope_moves_between_single_and_multi_sheet_views(client):
    workbook = openpyxl.Workbook()
    workbook.active.title = "Sales"
    workbook.active.append(["Revenue"])
    workbook.active.append([120])
    workbook.create_sheet("Costs").append(["Cost"])
    content = BytesIO()
    workbook.save(content)
    content.seek(0)
    client.post(
        "/upload",
        data={"excel_file": (content, "sample.xlsx"), "user_question": "Summarize"},
        content_type="multipart/form-data",
    )
    multi = client.post("/ask_another", data={"user_question": "How do they compare?", "analysis_scope": "all"})
    assert b"Workbook-wide answer" in multi.data
    assert b"Cross-sheet findings" in client.get("/result").data
    single = client.post("/ask_another", data={
        "user_question": "What is here?", "analysis_scope": "current", "target_sheet": "Costs",
    })
    assert b"Answer to your question" in single.data
    assert b"Costs" in client.get("/result").data


def test_invalid_scope_or_sheet_does_not_call_model(client, monkeypatch):
    client.post(
        "/upload",
        data={"excel_file": (workbook_bytes(), "sample.xlsx"), "user_question": "Summarize"},
        content_type="multipart/form-data",
    )
    monkeypatch.setattr(modelmind, "call_gemini_api", lambda prompt: pytest.fail("model called"))
    for form in (
        {"user_question": "Hello", "analysis_scope": "invalid"},
        {"user_question": "Hello", "analysis_scope": "current", "target_sheet": "Unknown"},
    ):
        assert client.post("/ask_another", data=form).status_code == 302


def test_large_workbook_is_rejected_before_model_call(client, monkeypatch):
    monkeypatch.setattr(modelmind, "call_gemini_api", lambda prompt: pytest.fail("model called"))
    oversized = BytesIO(b"x" * (15 * 1024 * 1024 + 1))
    response = client.post(
        "/upload",
        data={"excel_file": (oversized, "large.xlsx"), "user_question": "Summarize"},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"workbook under 15 MB" in response.data
