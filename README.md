# API Sentinel v1.0.0

**A Python-based API Security Testing Toolkit for Local Security Labs**

API Sentinel is a Python-based security testing project designed to demonstrate API authorization testing, BOLA/IDOR detection, OpenAPI specification auditing, HTTP security checks, regression testing, and security report generation.

The project uses intentionally configured local test fixtures to demonstrate authorization behavior in secure and vulnerable API scenarios.

> **Scope:** This project is intended for authorized security testing and local laboratory environments. Results from a local fixture do not establish that a public or production API is vulnerable.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Recorded Test Results](#recorded-test-results)
- [Reports](#reports)
- [Test Evidence](#test-evidence)
- [Security Methodology](#security-methodology)
- [Limitations](#limitations)
- [Responsible Use](#responsible-use)
- [Version](#version)
- [Author](#author)

## Features

### 1. BOLA / IDOR Scanner

- Compares authorization behavior between secure and intentionally vulnerable local API fixtures.
- Tests access to the authenticated user's own object.
- Tests attempts to access another user's object.
- Checks expected HTTP responses against actual responses.
- Identifies unauthorized object access in the vulnerable fixture.

### 2. OpenAPI Specification Audit

- Audits the configured API specification.
- Reports potential documentation issues detected by the implemented checks.
- Helps identify areas that may require manual specification review.

### 3. HTTP Security Checks

- Sends HTTP requests to configured local test endpoints.
- Records HTTP response status codes and content types.
- Supports inspection of endpoint behavior in the test environment.
- Helps document unexpected responses for further review.

### 4. Auth-Aware BOLA Tests

Tests authorization behavior using scenarios such as:

- Authenticated user accessing their own order.
- Authenticated user attempting to access another user's order.
- Different authenticated user accessing their own order.
- Unauthenticated request.
- Invalid authentication token.
- Request for a nonexistent order.

### 5. Regression Testing

- Checks implemented test scenarios and expected results.
- Helps detect unexpected changes in the project's recorded test behavior.
- Provides a repeatable command for running the available regression suite.

### 6. Security Report Generation

The project can generate reports in supported formats, including:

- JSON
- Markdown
- HTML

Generated reports depend on which tests and report-generation options have been executed.

## Project Structure

The following is an illustrative structure. Actual files may differ depending on the current repository contents and generated reports.

```text
api-sentinel/
├── src/
│   ├── cli.py
│   ├── mock_api.py
│   └── regression_test.py
├── reports/
│   ├── bola_comparison.json
│   ├── security_report_v1.0.0.md
│   ├── security_report_v1.0.0.html
│   ├── http_check.json
│   ├── auth_bola_report.json
│   ├── auth_bola_report.md
│   └── auth_bola_report.html
├── docs/
│   └── evidence/
│       ├── README.md
│       ├── regression-test-19-19.png
│       ├── bola-idor-scanner.png
│       ├── http-security-checks.png
│       ├── http-security-checks1.png
│       ├── security-report-html.png
│       ├── security-report-html1.png
│       └── security-report-html2.png
├── requirements.txt
└── README.md
```

Some report or evidence files may only appear after running the corresponding tests or copying screenshots into the repository.

## Requirements

- Python 3
- pip
- Git
- A terminal environment such as Kali Linux or another compatible Linux distribution
- Dependencies listed in `requirements.txt`

The exact dependency versions are defined by the repository's requirements file.

## Installation

Clone the repository:

```bash
git clone https://github.com/draxbae/api-sentinel.git
cd api-sentinel
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Launch the command-line interface:

```bash
python src/cli.py
```

The recorded CLI menu includes the following options:

1. BOLA / IDOR Scanner (local lab)
2. OpenAPI Specification Audit
3. HTTP Security Checks (localhost only)
4. View Reports
5. Generate HTML and Markdown Reports
6. Exit
7. Auth-Aware BOLA Tests
8. Generate Auth-Aware BOLA Reports

Choose the appropriate menu option and follow the prompts.

### Running Regression Tests

```bash
python src/regression_test.py
```

### Running Local BOLA / IDOR Tests

Select option 1 in the CLI.

The scanner starts or uses the configured local fixtures, compares authorization responses, and generates the corresponding comparison report when execution completes successfully.

Make sure the required local ports are available before running the scanner.

### Running the OpenAPI Audit

Select option 2 in the CLI.

Review the output and inspect the generated or configured specification as needed.

### Running HTTP Security Checks

Select option 3 in the CLI.

Run this option only against the configured local test service. Ensure that the service is running before starting the checks.

### Running Auth-Aware BOLA Tests

Select option 7 in the CLI.

Review the output to verify the expected behavior of authentication and object-ownership scenarios.

### Generating Reports

Use options 4, 5, and 8 to view available reports or generate the supported HTML, Markdown, and authentication-aware BOLA reports.

## Recorded Test Results

The following results were recorded during previous local test runs for this project.

| Test | Recorded result |
|---|---|
| Regression suite | 19/19 checks passed |
| Auth-aware BOLA tests | 6/6 scenarios passed |
| OpenAPI specification audit | 0 potential documentation issues reported |
| Secure local fixture | Unauthorized cross-user order access was rejected |
| Vulnerable local fixture | Cross-user order access was detected |

### BOLA / IDOR Demonstration

The recorded local comparison detected a case in which Alice could read Bob's order in the intentionally vulnerable fixture.

- Endpoint: `GET /orders/1002`
- Object ID: `1002`
- Expected response for unauthorized access: `403 Forbidden`
- Actual response in the vulnerable fixture: `200 OK`
- Recorded result: `FINDING`

The secure fixture rejected the unauthorized request, while the vulnerable fixture demonstrated the authorization failure intentionally configured for the lab.

These results describe the recorded test runs. They do not prove that all project components are secure or that any external service has the same vulnerability.

## Reports

The recorded test workflow produced or referenced reports including:

- `reports/bola_comparison.json`
- `reports/security_report_v1.0.0.md`
- `reports/security_report_v1.0.0.html`
- `reports/http_check.json`
- `reports/auth_bola_report.json`
- `reports/auth_bola_report.md`
- `reports/auth_bola_report.html`

Report availability depends on the tests executed and the current contents of the `reports/` directory.

Review reports before sharing them publicly. Remove credentials, tokens, personal data, internal addresses, or other sensitive information if present.

## Test Evidence

Screenshots from local security testing are stored in [`docs/evidence/`](docs/evidence/).

See the [evidence index](docs/evidence/README.md) for descriptions of the screenshots and the scope of the demonstrations.

Expected evidence filenames include:

- `regression-test-19-19.png`
- `bola-idor-scanner.png`
- `http-security-checks.png`
- `http-security-checks1.png`
- `security-report-html.png`
- `security-report-html1.png`
- `security-report-html2.png`

Only files that actually exist in the repository will be displayed on GitHub. Additional screenshots can document different sections of a long terminal output or report.

## Security Methodology

API Sentinel demonstrates several practical API security testing concepts.

### Object-Level Authorization

Changing an object identifier must not grant access to another user's data. The API must validate authorization on the server side for every protected object.

### Authentication Handling

Requests without valid authentication should receive an appropriate rejection when authentication is required.

### Expected Versus Actual Responses

The scanner compares expected status codes with actual responses to identify potentially unexpected authorization behavior.

### Manual Validation

Automated findings should be reviewed manually in the authorized test environment before being treated as confirmed vulnerabilities.

## Limitations

- Tests cover only the implemented scenarios and configured test environment.
- Regression tests do not establish that the complete application is free of defects.
- An OpenAPI audit reporting zero potential documentation issues does not prove that the API implementation is secure.
- HTTP status codes alone cannot establish the absence of vulnerabilities.
- Automated tools can produce false positives and false negatives.
- CVSS scores require a separate, documented risk assessment; no score is claimed here.
- Local fixture results must not be represented as findings against a real production target.

## Responsible Use

Use API Sentinel only against systems you own or have explicit authorization to test.

- Keep testing within the agreed scope.
- Prefer local fixtures and designated staging environments.
- Avoid accessing, modifying, or disclosing other users' data.
- Preserve relevant evidence and document test conditions.
- Report verified findings through the system owner's approved security reporting process.

## Version

**Current documented version:** v1.0.0

This README documents the project's recorded capabilities and test results. Confirm repository files and test outputs before publishing a release or making claims about current functionality.

## Author

Developed as a cybersecurity portfolio project focused on API security testing, BOLA/IDOR demonstrations, authorization validation, and security reporting.

Repository: [draxbae/api-sentinel](https://github.com/draxbae/api-sentinel)
