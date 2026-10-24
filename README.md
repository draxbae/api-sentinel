# API Sentinel

**Local API Security Testing Toolkit — BOLA/IDOR Detection**

API Sentinel is a Python-based security testing project for evaluating API authorization behavior using controlled local fixtures. It compares a secure mock API with an intentionally vulnerable lab API and generates security assessment reports.

## Features

- BOLA/IDOR authorization testing
- Secure API versus vulnerable lab comparison
- HTTP authentication and authorization checks
- Regression tests for expected security behavior
- JSON, Markdown, and HTML security reports
- OpenAPI specification auditing
- Local-only testing environment

## Project Structure

```text
api-sentinel/
├── backups/
├── examples/
│   └── openapi.yaml
├── reports/
│   ├── bola_comparison.json
│   ├── security_report_v0.8.0.md
│   └── security_report_v0.8.0.html
└── src/
    ├── bola_test.py
    ├── html_report.py
    ├── markdown_report.py
    ├── mock_api.py
    ├── mock_api_vulnerable_lab.py
    ├── regression_test.py
    ├── sentinel.py
    └── spec_audit.py
```

## Requirements

- Python 3
- Python virtual environment
- `httpx`
- `PyYAML`

Install dependencies in your virtual environment:

```bash
pip install httpx PyYAML
```

## Run the Local Lab

Open separate terminals for the two local mock APIs.

**Terminal 1 — Secure API**

```bash
cd ~/api-sentinel
source .venv/bin/activate
python -u src/mock_api.py
```

**Terminal 2 — Intentionally vulnerable lab API**

```bash
cd ~/api-sentinel
source .venv/bin/activate
python src/mock_api_vulnerable_lab.py
```

Use these fixtures only on your own machine or in an explicitly authorized environment.

## Run the Tests

In a third terminal:

```bash
cd ~/api-sentinel
source .venv/bin/activate

python src/bola_test.py
python src/regression_test.py
python src/markdown_report.py
python src/html_report.py
```

## Latest Lab Results

The current local lab comparison contains eight test cases:

- Secure fixture: four tests passed.
- Vulnerable fixture: three tests passed and one potential BOLA/IDOR finding was detected.
- Regression tests: four checks passed.

The potential finding occurs when Alice receives Bob's order data despite the expected HTTP status being `403`; the lab returns `200`.

## Reports

Generated reports are available in the `reports/` directory:

- `security_report_v0.8.0.md` — Markdown report
- `security_report_v0.8.0.html` — HTML report
- `bola_comparison_v0.8.0.json` — structured test results

Open the HTML report in a browser:

```bash
firefox reports/security_report_v0.8.0.html
```

## Security Recommendation

APIs should enforce server-side authorization and object ownership checks on every request. Authentication alone does not guarantee that a user is allowed to access a particular object.

## Scope and Disclaimer

This project is intended for educational use and authorized security testing. The vulnerable API is an intentionally configured local fixture. Its behavior is not evidence of a vulnerability in any production system.

Do not test systems without explicit permission.

## Current Version

**Documentation version:** 0.8.0
