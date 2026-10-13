"""Test the limited FHIR R4 checks independently of the legacy agent audit."""
import json
from bundle_validation import validate_bundle
from cli import main
from agents.api import api_validate


def bundle(kind="collection", entries=None):
    return {"resourceType": "Bundle", "type": kind, "entry": entries if entries is not None else []}


def codes(report):
    return {issue["code"] for issue in report["issues"]}


def test_empty_collection_and_api():
    data = bundle()
    assert validate_bundle(data)["valid"] is True
    assert api_validate(data)["errorCount"] == 0


def test_document_and_message_requirements():
    data = bundle("document", [{"resource": {"resourceType": "Patient"}}])
    assert {"bdl-9", "bdl-10", "bdl-11"} <= codes(validate_bundle(data))
    assert "bdl-12" in codes(validate_bundle(bundle("message")))


def test_request_response_search_and_total():
    assert "bdl-3" in codes(validate_bundle(bundle("transaction", [{"resource": {"resourceType": "Patient"}}])))
    assert validate_bundle(bundle("batch-response", [{"response": {"status": "200 OK"}}]))["valid"]
    assert "bdl-2" in codes(validate_bundle(bundle("collection", [{"search": {"mode": "match"}, "resource": {"resourceType": "Patient"}}])))
    data = bundle()
    data["total"] = True
    assert {"bdl-1", "TOTAL"} <= codes(validate_bundle(data))


def test_fullurl_duplicate_and_contained_reference():
    entry = {"fullUrl": "urn:uuid:patient", "resource": {"resourceType": "Patient", "id": "p"}}
    assert "bdl-7" in codes(validate_bundle(bundle(entries=[entry, entry])))
    versioned = {"fullUrl": "https://example.test/Patient/p/_history/1", "resource": {"resourceType": "Patient"}}
    assert "bdl-8" in codes(validate_bundle(bundle(entries=[versioned])))
    ref = {"resource": {"resourceType": "Observation", "subject": {"reference": "#missing"}}}
    result = validate_bundle(bundle(entries=[ref]))
    assert result["valid"] and result["warningCount"] == 1


def test_cli_json_reports(tmp_path, capsys):
    inp = tmp_path / "example.json"
    out = tmp_path / "report.json"
    inp.write_text(json.dumps(bundle()), encoding="utf-8")
    assert main(["validate", "-i", str(inp), "-o", str(out)]) == 0
    assert json.loads(out.read_text())["valid"] is True
    inp.write_text(json.dumps(bundle("bad")), encoding="utf-8")
    assert main(["validate", "-i", str(inp)]) == 1
    inp.write_text("{malformed", encoding="utf-8")
    assert main(["validate", "-i", str(inp)]) == 2
