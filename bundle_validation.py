"""Dependency-free subset of HL7 FHIR R4 Bundle structural invariants.

This is not an implementation-guide profile, resource-schema, terminology, or
clinical validator. External references may legitimately be unresolved.
"""
import re

TYPES = {"document", "message", "transaction", "transaction-response", "batch",
         "batch-response", "history", "searchset", "collection"}
REQ = {"batch", "transaction", "history"}
RESP = {"batch-response", "transaction-response", "history"}
FHIR_ID = re.compile(r"^[A-Za-z0-9.-]{1,64}$")
RELATIVE_REF = re.compile(r"^[A-Z][A-Za-z0-9]+/[A-Za-z0-9.-]+$")
URN_REF = re.compile(r"^urn:(uuid|oid):", re.I)


def _obj(value):
    return isinstance(value, dict)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def validate_bundle(bundle):
    """Return error/warning report for a parsed JSON-compatible Bundle object."""
    issues = []
    entries = []
    identities = set()
    seen = set()
    count = 0

    def add(severity, path, code, message):
        issues.append(dict(severity=severity, path=path, code=code, message=message))

    def err(path, code, message):
        add("error", path, code, message)

    def warn(path, code, message):
        add("warning", path, code, message)

    if not _obj(bundle):
        err("$", "STRUCTURE", "Expected a JSON object representing a FHIR Bundle.")
        return dict(valid=False, resourceCount=0, errorCount=1, warningCount=0, issues=issues)
    if bundle.get("resourceType") != "Bundle":
        err("$.resourceType", "RESOURCE_TYPE", "resourceType must be Bundle.")
    bundle_type = bundle.get("type")
    if bundle_type not in TYPES if isinstance(bundle_type, str) else True:
        err("$.type", "BUNDLE_TYPE", "Unknown FHIR R4 Bundle type.")
    if "id" in bundle and (not isinstance(bundle["id"], str) or not FHIR_ID.fullmatch(bundle["id"])):
        err("$.id", "FHIR_ID", "Invalid Bundle id; expected 1–64 letters, numbers, hyphens, or periods.")
    if "entry" in bundle and not isinstance(bundle["entry"], list):
        err("$.entry", "ENTRY_TYPE", "entry must be an array.")
    if isinstance(bundle.get("entry"), list):
        entries = bundle["entry"]
    if "total" in bundle:
        if bundle_type not in ("history", "searchset"):
            err("$.total", "bdl-1", "total is allowed only for searchset/history.")
        if type(bundle["total"]) is not int or bundle["total"] < 0:
            err("$.total", "TOTAL", "total must be a non-negative integer.")
    if bundle_type == "document":
        identifier = bundle.get("identifier")
        if not _obj(identifier) or not _text(identifier.get("system")) or not _text(identifier.get("value")):
            err("$.identifier", "bdl-9", "Document requires identifier.system and identifier.value.")
        if not _text(bundle.get("timestamp")):
            err("$.timestamp", "bdl-10", "Document requires timestamp.")
        first = entries[0] if entries else None
        if not _obj(first) or not _obj(first.get("resource")) or first["resource"].get("resourceType") != "Composition":
            err("$.entry[0].resource", "bdl-11", "First document entry must contain Composition.")
    if bundle_type == "message":
        first = entries[0] if entries else None
        if not _obj(first) or not _obj(first.get("resource")) or first["resource"].get("resourceType") != "MessageHeader":
            err("$.entry[0].resource", "bdl-12", "First message entry must contain MessageHeader.")
    for i, entry in enumerate(entries):
        path = "$.entry[%d]" % i
        if not _obj(entry):
            err(path, "ENTRY_TYPE", "Entry must be an object.")
            continue
        request, response, resource = ("request" in entry, "response" in entry, "resource" in entry)
        if not (request or response or resource):
            err(path, "bdl-5", "Entry needs resource, request, or response.")
        if request != (bundle_type in REQ):
            err(path + ".request", "bdl-3", "Invalid request presence for Bundle.type.")
        if response != (bundle_type in RESP):
            err(path + ".response", "bdl-4", "Invalid response presence for Bundle.type.")
        if "search" in entry and bundle_type != "searchset":
            err(path + ".search", "bdl-2", "entry.search only allowed in searchset.")
        if request:
            req = entry["request"]
            if not _obj(req) or req.get("method") not in ("GET", "HEAD", "POST", "PUT", "DELETE", "PATCH") or not _text(req.get("url")):
                err(path + ".request", "REQUEST", "request requires a recognized HTTP method and URL.")
        if response:
            resp = entry["response"]
            if not _obj(resp) or not _text(resp.get("status")):
                err(path + ".response", "RESPONSE", "response.status is required.")
        if "fullUrl" in entry:
            url = entry["fullUrl"]
            if not _text(url):
                err(path + ".fullUrl", "FULL_URL", "fullUrl must be a nonempty string.")
            else:
                if "/_history/" in url:
                    err(path + ".fullUrl", "bdl-8", "fullUrl may not be version-specific.")
                res = entry.get("resource")
                meta = res.get("meta") if _obj(res) else None
                version = meta.get("versionId") if _obj(meta) else None
                key = (url, str(version) if version is not None else "")
                if bundle_type != "history" and key in seen:
                    err(path + ".fullUrl", "bdl-7", "Duplicate fullUrl and resource version.")
                seen.add(key)
                identities.add(url)
        if resource:
            res = entry["resource"]
            if not _obj(res) or not _text(res.get("resourceType")):
                err(path + ".resource.resourceType", "RESOURCE_TYPE", "resourceType must be a nonempty string.")
            else:
                count += 1
                rid = res.get("id")
                if "id" in res and (not isinstance(rid, str) or not FHIR_ID.fullmatch(rid)):
                    err(path + ".resource.id", "FHIR_ID", "Invalid resource id.")
                if _text(rid):
                    identities.add(res["resourceType"] + "/" + rid)
    for i, entry in enumerate(entries):
        if not _obj(entry) or not _obj(entry.get("resource")):
            continue
        resource = entry["resource"]
        contained = {r.get("id") for r in resource.get("contained", [])
                     if _obj(r) and _text(r.get("id"))} if isinstance(resource.get("contained"), list) else set()

        def visit(value, path, depth=0):
            if depth > 40:
                return
            if isinstance(value, list):
                for j, v in enumerate(value):
                    visit(v, path + "[%d]" % j, depth + 1)
            elif _obj(value):
                ref = value.get("reference")
                if _text(ref):
                    if ref.startswith("#") and ref[1:] not in contained:
                        warn(path + ".reference", "CONTAINED_REF", "Unresolved contained reference.")
                    elif (URN_REF.match(ref) or RELATIVE_REF.fullmatch(ref)) and ref not in identities:
                        warn(path + ".reference", "EXTERNAL_REF", "Unresolved within this Bundle; external references may be valid.")
                for key, child in value.items():
                    if key != "contained":
                        visit(child, path + "." + str(key), depth + 1)
        visit(resource, "$.entry[%d].resource" % i)
    errors = sum(x["severity"] == "error" for x in issues)
    return dict(valid=errors == 0, resourceCount=count, errorCount=errors,
                warningCount=len(issues) - errors, issues=issues)
