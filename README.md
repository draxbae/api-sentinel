# API Sentinel

**API Security Testing Toolkit for BOLA/IDOR Detection**

API Sentinel is a Python-based toolkit for learning and testing API authorization security in a controlled local environment. It demonstrates Broken Object Level Authorization (BOLA), also known as IDOR, by comparing a secure mock API with an intentionally vulnerable lab API.

## Features

- BOLA/IDOR testing against local mock APIs.
- Comparison between secure and intentionally vulnerable authorization behavior.
- Authentication-aware test scenarios.
- OpenAPI specification auditing.
- HTTP security checks restricted to localhost.
- Regression testing.
- JSON, Markdown, and HTML report generation.
- Interactive command-line interface.
- Evidence and report review workflow.

## Requirements

- Python 3.9 or later with support for the syntax used by the project.
- Git.
- Linux, macOS, or another environment that supports Python virtual environments.
- Network access to install dependencies, unless they are already available locally.

Use a Python version compatible with the project's dependencies and source code.

## Installation

Clone the repository:

```bash
git clone https://github.com/draxbae/api-sentinel.git
cd api-sentinel
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Usage

Start the interactive CLI:

```bash
python src/cli.py
```

The CLI provides the following options:

1. **BOLA / IDOR Scanner (local lab)** — starts the local secure and vulnerable fixtures, runs the BOLA tests and regression tests, and generates reports.
2. **OpenAPI Specification Audit** — audits the example OpenAPI specification.
3. **HTTP Security Checks (localhost only)** — runs HTTP checks against an accepted localhost URL.
4. **View Reports** — displays available report files.
5. **Generate HTML and Markdown Reports** — generates report outputs.
6. **Exit** — exits the application.
7. **Auth-Aware BOLA Tests** — runs the authentication-aware BOLA test module.
8. **Generate Auth-Aware BOLA Reports** — generates reports for authentication-aware tests.

Menu options may depend on the version of the repository you are using.

## Local Testing Environment

API Sentinel provides two mock API fixtures for local authorization testing.

| Fixture | Address | Purpose |
|---|---|---|
| `src/mock_api.py` | `http://127.0.0.1:8000` | Secure API fixture that checks order ownership |
| `src/mock_api_vulnerable_lab.py` | `http://127.0.0.1:8001` | Intentionally vulnerable fixture that does not check order ownership |

Both fixtures bind to the loopback interface (`127.0.0.1`) and are intended for local testing.

### Run the Integrated BOLA Lab

1. Activate the project's virtual environment.
2. Ensure ports `8000` and `8001` are available.
3. Start the CLI:

   ```bash
   python src/cli.py
   ```

4. Select option `1`, **BOLA / IDOR Scanner (local lab)**.
5. Let the CLI start the fixtures and run the tests.
6. Review the output and generated files in `reports/`.

The CLI checks whether the required ports are available before starting the fixtures. It starts both local APIs, runs `bola_test.py`, then runs `regression_test.py`. If the workflow finishes or is interrupted, the CLI attempts to stop the fixture processes it started.

Do not start separate fixture processes on ports `8000` or `8001` before using this integrated workflow.

### How the Lab Demonstrates BOLA

The lab contains two sample orders:

- Order `1001` belongs to Alice.
- Order `1002` belongs to Bob.

The fixtures use the following example bearer tokens:

- `alice-token`
- `bob-token`

The secure fixture checks whether the authenticated user owns the requested order. An attempt by Alice to access Bob's order should be denied.

The vulnerable fixture authenticates the user but does not check order ownership. This intentionally demonstrates how an authenticated user may access another user's order by changing the object identifier.

These tokens and records are test data for the local lab only. They are not real credentials.

## Running Tests Separately

Run the regression test suite:

```bash
python src/regression_test.py
```

Run the authentication-aware BOLA test module:

```bash
python src/auth_bola_test.py
```

Generate authentication-aware reports:

```bash
python src/auth_report.py
```

Run these commands from the repository root with the virtual environment activated.

**Important:** The integrated CLI workflow is the recommended starting point for the BOLA lab. Before running a test module independently, inspect its implementation to confirm whether it starts its own fixtures or requires the local APIs to be running.

## HTTP Security Checks

Select option `3` in the CLI to run HTTP security checks.

The CLI is designed to accept HTTP URLs on `localhost` or `127.0.0.1`, for example:

```text
http://127.0.0.1:8000
```

Public domains, HTTPS URLs, and non-local network addresses are not accepted by this CLI option.

## OpenAPI Specification Audit

Select option `2` to audit the example specification:

```text
examples/openapi.yaml
```

The specification audit checks the documented API definition. A finding in an OpenAPI specification is not, by itself, proof that a live API endpoint is vulnerable.

## Reports and Evidence

Generated reports and lab logs are stored in the `reports/` directory. Depending on the modules executed, files may include:

- `bola_comparison.json`
- `secure_lab.log`
- `vulnerable_lab.log`
- Markdown reports
- HTML reports
- Authentication-aware test reports

The CLI's report center can display available report files. HTML reports can be opened in a browser using the local file path shown by the application.

Report filenames and generated artifacts may vary depending on the modules executed and the repository version.

## Project Structure

```text
api-sentinel/
├── .github/
│   └── workflows/
├── examples/
│   └── openapi.yaml
├── reports/
├── src/
│   ├── auth_bola_test.py
│   ├── auth_report.py
│   ├── bola_test.py
│   ├── cli.py
│   ├── http_checker.py
│   ├── markdown_report.py
│   ├── mock_api.py
│   ├── mock_api_vulnerable_lab.py
│   ├── regression_test.py
│   └── spec_audit.py
├── .gitignore
├── README.md
└── requirements.txt
```

This is a high-level overview. The repository may contain additional files or directories.

## Testing Scope and Limitations

API Sentinel is an educational and testing toolkit, not a guarantee that an API is secure.

- Results depend on the test scenarios, configuration, and code being tested.
- The local mock APIs are simplified fixtures and do not represent every real-world API architecture.
- OpenAPI specification findings do not automatically establish runtime vulnerabilities.
- A passing regression suite does not prove that all security issues have been eliminated.
- Generated reports should be reviewed before being used as formal security evidence.

## Responsible Use

Use API Sentinel only against systems you own or have explicit authorization to test.

Keep the intentionally vulnerable fixture isolated to the local testing environment. Do not expose it to a public network or deploy it as a production service.

Do not use this project as authorization to test third-party systems.

## Disclaimer

The author provides this project for educational, defensive security testing, and authorized assessment purposes. Users are responsible for complying with applicable laws, rules, and authorization requirements.
