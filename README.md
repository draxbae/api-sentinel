# API Sentinel

**Local API Security Testing Toolkit — BOLA/IDOR Detection**

API Sentinel is a Python-based security testing toolkit for evaluating API authorization behavior in controlled local environments. It compares a secure mock API with an intentionally vulnerable lab API and generates security assessment reports.

## Features

- BOLA (Broken Object Level Authorization) and IDOR testing
- Secure versus intentionally vulnerable local API comparison
- Authentication-aware authorization test scenarios
- HTTP security checks restricted to localhost
- OpenAPI specification auditing
- Regression testing for expected security behavior
- JSON, Markdown, and HTML security reports
- Interactive command-line interface (CLI)
- Evidence-based security assessment workflow
- Controlled local testing environment

## Requirements

- Python 3
- Git
- Linux, macOS, or another environment capable of running Python
- Network access only when installing project dependencies

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/draxbae/api-sentinel.git
cd api-sentinel
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Start the interactive CLI:

```bash
python src/cli.py
```

The CLI provides options for:

1. BOLA / IDOR scanning against the local lab
2. OpenAPI specification auditing
3. HTTP security checks restricted to localhost
4. Viewing available reports
5. Generating HTML and Markdown reports
6. Exiting the application
7. Running authentication-aware BOLA tests
8. Generating authentication-aware BOLA reports

The available features depend on the scripts and configuration included in the repository version you are using.

## Testing

### Regression Tests

Run the regression test suite:

```bash
python src/regression_test.py
```

This checks the expected behavior of the project's local security testing scenarios.

### Authentication-Aware BOLA Tests

Run the authentication-aware test suite:

```bash
python src/auth_bola_test.py
```

These tests exercise authorization scenarios using the project's controlled fixtures, including permitted access, denied cross-user access, invalid authentication, and missing resources.

### Generate Authentication-Aware Reports

Run:

```bash
python src/auth_report.py
```

Review the generated output to inspect the evidence and findings produced by the tests.

## Reports and Evidence

The `reports/` directory contains generated security assessment artifacts. Depending on the tests run, these may include:

- JSON evidence and structured results
- Markdown security reports
- HTML security reports
- Secure-versus-vulnerable API comparison results
- HTTP security check results
- Authentication-aware BOLA test reports

Reports reflect the state of the test environment at the time they were generated. Review and validate the evidence before using it in a formal security assessment.

## Project Structure

```text
api-sentinel/
├── src/
│   ├── auth_bola_test.py
│   ├── auth_report.py
│   ├── bola_test.py
│   ├── cli.py
│   ├── html_report.py
│   ├── http_checker.py
│   ├── markdown_report.py
│   ├── mock_api.py
│   ├── mock_api_vulnerable_lab.py
│   ├── openapi_parser.py
│   ├── regression_test.py
│   ├── report_generator.py
│   ├── report_v07.py
│   ├── sentinel.py
│   └── spec_audit.py
├── reports/
├── requirements.txt
└── README.md
```

The files listed above describe the main components. Additional files may exist in the repository.

## Testing Scope

API Sentinel is designed for controlled API security assessment. Its local fixtures help evaluate whether authorization rules behave as expected, particularly when users attempt to access objects belonging to other users.

A passing test suite demonstrates the expected behavior of the tested scenarios; it does not prove that every possible vulnerability has been eliminated.

## Responsible Use

- Test only systems you own or have explicit permission to assess.
- Prefer the included local fixtures and lab APIs for experimentation.
- Do not send test payloads to public systems without authorization.
- Protect tokens, credentials, personal information, and security evidence.
- Validate findings before reporting them to the relevant system owner.

## Limitations

Results depend on the configured fixtures, test scenarios, and available evidence. Automated checks may produce false positives or false negatives and should be supplemented with manual review.

Risk ratings and severity assessments should be supported by evidence and reviewed before being treated as final.

## Disclaimer

API Sentinel is provided for educational and authorized security testing purposes. Users are responsible for obtaining appropriate authorization and complying with applicable laws, regulations, and program rules.
