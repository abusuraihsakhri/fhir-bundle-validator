# FHIR Bundle Validator

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

FHIR R4 Bundle Validator is a clinical decision support tool that provides:

- **PHI Outbound Guard:** AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers
- **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation
- **Multi-Agent Worker System:** Specialized workers for QC, safety escalation, and protocol conformance
- **FastAPI REST API:** OpenAPI 3.1 endpoints with Prometheus-compatible metrics
- **Batch CSV Processing:** Process multiple records with lookup scoring

---

## ⚙️ Key Capabilities & Algorithmic Modules

### Security & Audit
- **PHI Guard:** Pattern-based detection and redaction of protected health information
- **Audit Trail:** HMAC-SHA256 chained logging with integrity verification

### Worker Agents
- **InvariantQCWorker:** Primary metric threshold monitoring
- **SafetyEscalationWorker:** Critical safety interlock detection
- **ProtocolConformanceWorker:** Spec conformance and anomaly triage

### Enrichment Engines
- Features Engine, Real-Time Monitoring Dashboard, Automated Escalation Protocol
- Multi-Site Deployment Framework, Clinical Workflow Integration
- Predictive Analytics Engine, Patient Outcome Tracking

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/fhir-bundle-validator.git
cd fhir-bundle-validator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## 🚀 Usage

### CLI Commands

```bash
# Run single task evaluation
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2

# Batch process CSV records
python cli.py batch -i input.csv -o results.csv

# Verify audit trail integrity
python cli.py verify-audit

# Launch FastAPI REST server
python cli.py serve --host 127.0.0.1 --port 8000

# Interactive chat query
python cli.py chat "Explain specifications"
```

### FHIR Validator Module

```bash
# Single lookup
python -m fhir_validator single creatinine

# Batch CSV processing
python -m fhir_validator batch --input sample.csv --output results.csv
```

### REST API Endpoints

| Endpoint | Method | Description |
|:---------|:-------|:------------|
| `/health` | GET | Service health check |
| `/metrics` | GET | Prometheus-compatible metrics |
| `/api/audit` | POST | Submit task for evaluation |
| `/api/chat` | POST | Query supervisory chat |
| `/api/audit/logs` | GET | Retrieve audit trail |

---

## 🛡️ Security Configuration

### Audit Secret Key

Set the `AUDIT_SECRET_KEY` environment variable for persistent audit integrity:

```bash
export AUDIT_SECRET_KEY="your-secure-random-key"
```

**Warning:** Without this key, an ephemeral session key is generated, and audit integrity cannot be verified across restarts.

### PHI Protection

The system automatically blocks outbound data containing:
- Medical Record Numbers (MRN)
- Social Security Numbers (SSN)
- Phone numbers and email addresses
- Patient names and dates of birth

---

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest -v --cov=.

# Run specific test modules
pytest tests/test_fhir_bundle_validator.py -v
pytest tests/test_enrichment.py -v
pytest test_fhir_validator.py -v
```

### Test Coverage

- PHI guard enforcement and redaction
- Worker agent evaluation logic
- Supervisor consensus and audit trail
- Audit integrity verification (tamper detection)
- CLI command processing
- CSV batch processing
- Enrichment engine threshold evaluation

---

## 🐳 Docker Deployment

```bash
docker build -t fhir-bundle-validator .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY="your-key" fhir-bundle-validator
```

---

## 📁 Project Structure

```
fhir-bundle-validator/
├── agents/                  # Multi-agent worker system
│   ├── api.py              # FastAPI REST server
│   ├── base.py             # Security, PHI guard, audit trail
│   ├── models.py           # Pydantic data models
│   ├── supervisor.py       # Master orchestrator
│   ├── workers.py          # Specialized worker agents
│   ├── llm_factory.py      # LLM provider factory
│   ├── learning.py         # Bayesian calibration engine
│   ├── metrics.py          # Prometheus metrics collector
│   └── streamer.py         # WebSocket telemetry
├── tests/                  # Test suite
├── cli.py                  # Command-line interface
├── fhir_validator.py       # FHIR validation module
├── enrichment.py           # Enrichment engine suite
├── simulator.py            # High-throughput stress tester
├── Dockerfile              # Container configuration
└── docker-compose.yml      # Multi-service orchestration
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
