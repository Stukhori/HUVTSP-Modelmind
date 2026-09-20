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
