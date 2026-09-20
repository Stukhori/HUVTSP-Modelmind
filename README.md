# ModelMind

ModelMind is a Flask prototype for asking natural-language questions about an Excel workbook. It reads one worksheet or compares multiple worksheets, shows a five-row preview and simple diagnostics, and sends a data summary and question to Gemini for a formatted answer. Answers should be checked against the workbook; this is not a financial-advice or production data-governance system.

## Run locally

Use Python 3.11 in a virtual environment, then install the packages used by `app.py`:

```bash
python -m pip install Flask pandas openpyxl google-generativeai Markdown
```

Set `GOOGLE_API_KEY` in the environment **before** starting the app. The application does not automatically load a `.env` file.

```powershell
$env:GOOGLE_API_KEY = "your-key"
python app.py
```

On macOS or Linux, use `export GOOGLE_API_KEY="your-key"` instead. Open `http://127.0.0.1:8080/` in a browser. The repository currently uses the legacy `google-generativeai` client and the `gemini-1.5-flash` model; API availability and account access must be checked separately.

## Workflow

1. Upload one `.xlsx` workbook under 15 MB and ask an initial question. `.xls` files are not supported by the configured reader.
2. Review the answer beside the sheet preview, numeric sums, error report, and trend summary. For a formula, ask for a specific reference such as “What is the formula in cell B2?”
3. Ask a follow-up about the current worksheet or explicitly compare all worksheets. In the workbook-wide view, select a worksheet to focus the next question.
4. Use the workbook navigation to inspect another sheet. Switching sheets changes the view; it does not generate an AI answer until you ask another question.
5. Return to the upload workspace to continue the current analysis, or choose **Start fresh** to clear its session and remove the active uploaded file.

The app writes uploaded workbooks to its local `uploads/` directory while the analysis is active. Do not upload confidential data unless you are comfortable with local file storage and sending summarized workbook content to the configured Gemini service. Closing a browser tab does not guarantee that the server-side upload is removed; use **Start fresh** for the active workbook.

## Tests

```bash
python -m pip install pytest
python -m pytest -q tests
```

The tests replace Gemini calls with local fakes; they do not require an API key or send workbook data to an external service.
