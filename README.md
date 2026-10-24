# API Sentinel

**Local API Security Testing Toolkit — BOLA/IDOR Detection**

API Sentinel is a Python-based security testing toolkit for evaluating API authorization behavior using controlled local fixtures. It compares a secure mock API with an intentionally vulnerable lab API and generates security assessment reports.

## Features

- BOLA/IDOR authorization testing
- Secure API versus intentionally vulnerable lab comparison
- HTTP authentication and authorization checks
- Regression tests for expected security behavior
- JSON, Markdown, and HTML security reports
- OpenAPI specification auditing
- Local-only testing environment

## Project Structure

```text
api-sentinel/
├── .github/
│   └── workflows/
├── backups/
├── evidence/
│   ├── 01-regression-tests.png
│   ├── 02-bola-comparison.png
│   ├── 03-github-actions-success.png
│   └── 04-release-v0.8.0.png
├── examples/
│   └── openapi.yaml
├── reports/
│   ├── bola_comparison.json
│   ├── bola_comparison_v0.6.0.json
│   ├── bola_comparison_v0.8.0.json
│   ├── bola_report.json
│   ├── http_check.json
│   ├── security_report_v0.7.0.json
│   ├── security_report_v0.8.0.html
│   ├── security_report_v0.8.0.md
│   ├── security_report_v1.0.0.html
│   ├── security_report_v1.0.0.md
│   └── spec_audit.json
├── src/
│   ├── bola_test.py
│   ├── html_report.py
│   ├── markdown_report.py
│   ├── mock_api.py
│   ├── mock_api_vulnerable_lab.py
│   ├── regression_test.py
│   ├── sentinel.py
│   └── spec_audit.py
├── .gitignore
└── README.md
```

## Requirements

- Python 3
- Python virtual environment
- `httpx`
- `PyYAML`

Install dependencies inside your virtual environment:

```bash
cd ~/api-sentinel
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Local Lab

Run each API in a separate terminal.

### Terminal 1 — Secure API

```bash
cd ~/api-sentinel
source .venv/bin/activate
python -u src/mock_api.py
```

### Terminal 2 — Intentionally Vulnerable Lab API

```bash
cd ~/api-sentinel
source .venv/bin/activate
python src/mock_api_vulnerable_lab.py
```

Use the vulnerable fixture only in your own local lab or an explicitly authorized environment.

## Run the Tests

Open a third terminal after both APIs have started:

```bash
cd ~/api-sentinel
source .venv/bin/activate

python src/bola_test.py
python src/regression_test.py
python src/markdown_report.py
python src/html_report.py
```

Run the OpenAPI specification audit when needed:

```bash
python src/spec_audit.py
```

## Latest Lab Results

API Sentinel v1.0.0 includes six BOLA test cases for each local fixture.

- Secure fixture: six tests passed.
- Vulnerable lab fixture: five tests passed and one intentional BOLA finding detected.
- Regression tests: 19/19 checks passed in the latest local run.

The intentional finding occurs when Alice requests Bob's order. The secure fixture denies cross-owner access, while the vulnerable lab intentionally returns the order data.

These results apply only to the controlled local fixtures. They do not establish a vulnerability in any production API.

Test results and generated reports may change when the tests are run again.

## Reports

The `reports/` directory contains structured test results and generated reports:

| File | Purpose |
|---|---|
| `bola_comparison.json` | Current BOLA comparison results |
| `bola_comparison_v0.6.0.json` | BOLA comparison results for version 0.6.0 |
| `bola_comparison_v0.8.0.json` | BOLA comparison results for version 0.8.0 |
| `bola_report.json` | BOLA report data |
| `http_check.json` | HTTP check results |
| `security_report_v0.7.0.json` | Security report data for version 0.7.0 |
| `security_report_v0.8.0.md` | Historical Markdown security report for v0.8.0 |
| `security_report_v1.0.0.md` | Current Markdown security report for v1.0.0 |
| `security_report_v0.8.0.html` | Historical HTML security report for v0.8.0 |
| `security_report_v1.0.0.html` | Current HTML security report for v1.0.0 |
| `spec_audit.json` | OpenAPI specification audit results |

Open the HTML report in a browser:

```bash
firefox reports/security_report_v1.0.0.html
```

Report contents depend on the latest test results generated locally. Regenerate reports after running tests if you need updated results.

## Evidence

The `evidence/` directory contains screenshots documenting:

1. Regression test results
2. BOLA comparison results
3. Successful GitHub Actions workflow
4. GitHub Release v0.8.0

Browse the evidence on GitHub:

https://github.com/draxbae/api-sentinel/tree/main/evidence

## Continuous Integration and Release

The repository includes a GitHub Actions workflow for automated checks.

- Repository: https://github.com/draxbae/api-sentinel
- GitHub Actions: https://github.com/draxbae/api-sentinel/actions
- Latest release v1.0.0: https://github.com/draxbae/api-sentinel/releases/tag/v1.0.0
- Previous release v0.8.0: https://github.com/draxbae/api-sentinel/releases/tag/v0.8.0

## Security Recommendations

APIs should enforce server-side authorization and object ownership checks on every request. Authentication alone does not guarantee that a user is allowed to access a particular object.

Recommended practices include:

- Verify that the authenticated user is authorized to access each requested object.
- Deny cross-user access by default.
- Test authorization behavior with positive and negative cases.
- Keep regression tests for authorization controls.
- Avoid exposing sensitive data in API responses or logs.

## Scope and Disclaimer

API Sentinel is intended for education, local security testing, and explicitly authorized assessments.

The vulnerable API is an intentionally configured local fixture. Its behavior is not evidence of a vulnerability in any production system.

Do not test systems without explicit permission.

## Current Version

- Toolkit test version: 1.0.0
- Documentation version: 1.0.0
- Previous GitHub release: v0.8.0
