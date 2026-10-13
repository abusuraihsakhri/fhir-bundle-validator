# FHIR Bundle Validator

### [Open the Live Application →](https://abusuraihsakhri.github.io/fhir-bundle-validator/)

Validate selected HL7 FHIR R4 Bundle structural rules using a browser, Python CLI, or FastAPI. The existing threshold-based agent audit is retained as a separate legacy workflow.

## Features and limitations

- JSON Bundle root, type, entry structure, and resource identifier checks.
- Selected FHIR R4 Bundle invariants bdl-1–bdl-5 and bdl-7–bdl-12, including document/message entry order, transaction and batch requirements, and fullUrl uniqueness.
- Warnings for unresolved local contained, relative, and URN references; external references can legitimately be outside the Bundle.
- JSON report with issue severity, JSON path, and rule code.

**This is a partial structural checker**, not full FHIR R4 conformance validation. It does not enforce resource schemas, required clinical resource elements, StructureDefinition profiles, implementation guides, terminology bindings, or remote reference resolution. Passing is not clinical or interoperability certification.

## Browser app

Open the web/index.html file in a modern Chromium, Firefox, or Safari browser, or use GitHub Pages once deployed. Paste Bundle JSON or open a local .json file (maximum 5 MiB), select **Validate Bundle**, and optionally download the report. **Load example** uses synthetic data.

The static application processes input in browser memory, with no uploads, remote libraries, or persistent browser storage. Reports contain issue metadata, not full input JSON. Avoid identifiable patient data on shared devices.

The legacy console is web/audit.html; its audit button requires a running same-origin FastAPI server. It no longer fabricates results when the server is absent.

## Local use

Requires Python 3.10+; CI currently checks 3.10–3.12. Set up a virtual environment and install runtime dependencies:

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt

Run the actual Bundle validator:

    python cli.py validate -i bundle.json -o validation-report.json

Exit status: 0 for no structural errors, 1 for errors, and 2 for unreadable/invalid input. Run the API and same-origin web app:

    python cli.py serve --host 127.0.0.1 --port 8000

Open http://127.0.0.1:8000/ for the UI, http://127.0.0.1:8000/docs for generated API documentation, or POST a JSON Bundle object to /api/validate.

Legacy agent commands are audit, batch, chat, and verify-audit; endpoints include /api/audit, /api/chat, /api/audit/logs, /health, and /metrics (JSON counters). The historical python -m fhir_validator single/batch performs dictionary lookup, **not** FHIR validation.

## Docker

For a local, non-committed audit secret:

    python -c "import secrets; print('AUDIT_SECRET_KEY=' + secrets.token_hex(32))" > .env
    docker compose up --build

Compose binds only to 127.0.0.1:8000 by default. The legacy HMAC ledger is in memory; restart persistence requires retaining both records and key. Regex-based sensitive identifier detection is not comprehensive PHI de-identification. Do not expose the legacy API publicly without authentication, TLS, and review.

## Tests

    python -m pip install -r requirements.txt pytest
    python -m pytest -q
    node --test tests/test_browser_validator.cjs
    node --check web/validator.js
    node --check web/app.js
    docker build -t fhir-bundle-validator .

CI exercises Python 3.10, 3.11, 3.12, Node.js 22 browser logic, and Docker image builds. JavaScript runs natively in the browser; Pyodide is not required.

## Technology and license

Python 3, FastAPI, Pydantic 2, vanilla JavaScript, HTML, and CSS. MIT licensed; see [LICENSE](LICENSE). Bundle invariant definitions: [HL7 FHIR R4 Bundle](https://hl7.org/fhir/R4/bundle.html).
