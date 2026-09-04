"""
Automated Pytest Test Suite for Fhir Bundle Validator.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, AuditTrail, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_audit_trail_integrity_tampering():
    """Verify tampered audit trail fails integrity check."""
    trail = AuditTrail(secret_key="test-key-for-integrity")
    trail.log("test", "test_tier", "TEST_EVENT", {"data": "value1"})
    trail.log("test", "test_tier", "TEST_EVENT", {"data": "value2"})
    assert trail.verify_integrity() is True

    # Tamper with an entry
    if trail.logs:
        trail.logs[0]["payload_hash"] = "tampered_hash"
    assert trail.verify_integrity() is False


def test_audit_trail_requires_secret_key():
    """Verify AuditTrail uses ephemeral key when no secret provided."""
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        trail = AuditTrail(secret_key=None)
        # Should have issued a warning about ephemeral key
        assert any("AUDIT_SECRET_KEY" in str(warning.message) for warning in w)
    assert trail.secret_key != b""


def test_phi_guard_redaction():
    """Verify PHI redaction replaces sensitive data."""
    text = "Patient John Doe MRN-12345678 has appointment"
    redacted = PHIGuard.redact_phi(text)
    assert "12345678" not in redacted
    assert "REDACTED_IDENTIFIER" in redacted


def test_supervisor_phi_blocking():
    """Verify supervisor rejects PHI in task IDs."""
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="Patient MRN-12345678",
        target_identifier="KEY-01",
        primary_metric=10.0,
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)
