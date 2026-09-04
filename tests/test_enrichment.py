"""
Automated Pytest for fhir-bundle-validator Enrichment Modules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from enrichment import (
    EnrichmentResult,
    BaseEnrichmentEngine,
    FeaturesEngine,
    RealtimeMonitoringDashboardEngine,
    AutomatedEscalationProtocolEngine,
    MultisiteDeploymentFrameworkEngine,
    TamperevidentAuditTrailEngine,
    ClinicalWorkflowIntegrationEngine,
    PredictiveAnalyticsEngine,
    PatientOutcomeTrackingEngine,
    FhirbundlevalidatorEnrichmentSuite,
    enrichment_suite,
)

def test_enrichment_suite_execution():
    suite = FhirbundlevalidatorEnrichmentSuite()
    res = suite.execute_all(primary_val=0.5, secondary_val=0.2)
    assert len(res) >= 1
    for k, v in res.items():
        assert v.status in ["OPTIMAL", "WARNING", "CRITICAL_ALERT"]
        assert isinstance(v.recommendations, list)

def test_enrichment_threshold_escalation():
    suite = FhirbundlevalidatorEnrichmentSuite()
    res = suite.execute_all(primary_val=10.0, secondary_val=5.0)
    for k, v in res.items():
        assert v.status in ["WARNING", "CRITICAL_ALERT"]
        assert len(v.alerts) > 0

def test_base_engine_history_tracking():
    """Verify history is recorded after each evaluation."""
    engine = FeaturesEngine(threshold=1.0)
    assert len(engine.history) == 0
    engine.evaluate(0.5)
    engine.evaluate(1.5)
    assert len(engine.history) == 2
    assert engine.history[0].status == "OPTIMAL"
    assert engine.history[1].status == "WARNING"

def test_engine_respects_custom_threshold():
    """Verify custom threshold changes evaluation outcome."""
    engine = FeaturesEngine(threshold=5.0)
    res = engine.evaluate(8.0)  # Below 2x threshold
    assert res.status == "WARNING"
    res = engine.evaluate(3.0)  # Below threshold
    assert res.status == "OPTIMAL"

def test_enrichment_result_defaults():
    """Verify EnrichmentResult dataclass defaults."""
    r = EnrichmentResult()
    assert r.status == "OPTIMAL"
    assert r.score == 0.0
    assert r.alerts == []
    assert r.recommendations == []
    assert isinstance(r.timestamp, str)
