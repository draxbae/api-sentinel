#!/usr/bin/env python3
"""Generate HTML and Markdown reports for API Sentinel auth/BOLA tests."""

import html
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "reports" / "auth_bola_report.json"
HTML_OUT = ROOT / "reports" / "auth_bola_report.html"
MD_OUT = ROOT / "reports" / "auth_bola_report.md"


def load_report():
    if not SOURCE.is_file():
        raise SystemExit(
            f"Report not found: {SOURCE}\n"
            "Run python src/auth_bola_test.py first."
        )

    try:
        report = json.loads(SOURCE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read source report: {exc}")

    if not isinstance(report.get("results"), list):
        raise SystemExit("Invalid report: 'results' must be a list.")

    return report


def make_markdown(report):
    summary = report.get("summary", {})
    results = report["results"]

    lines = [
        "# API Sentinel — Auth-Aware BOLA Assessment",
        "",
        f"**Version:** {report.get('version', 'unknown')}",
        f"**Generated:** {report.get('generated_at', 'unknown')}",
        f"**Scope:** {report.get('scope', 'not specified')}",
        f"**Target:** `{report.get('target', 'not specified')}`",
        "",
        "## Summary",
        "",
        f"- Total tests: {summary.get('total', len(results))}",
        f"- Passed: {summary.get('pass', 0)}",
        f"- Failed: {summary.get('fail', 0)}",
        f"- Errors: {summary.get('error', 0)}",
        "",
        "## Test results",
        "",
        "| Test | Path | Expected | Actual | Result |",
        "|---|---|---:|---:|---|",
    ]

    for item in results:
        name = str(item.get("test", "")).replace("|", "\\|")
        path = str(item.get("path", "")).replace("|", "\\|")
        expected = item.get("expected_status", "—")
        actual = item.get("actual_status", item.get("result", "—"))
        result = item.get("result", "UNKNOWN")
        lines.append(
            f"| {name} | `{path}` | {expected} | {actual} | {result} |"
        )

    lines.extend(["", "## Evidence", ""])

    for item in results:
        lines.extend([
            f"### {item.get('test', 'Unnamed test')}",
            "",
            f"- Method: `{item.get('method', 'unknown')}`",
            f"- Path: `{item.get('path', 'unknown')}`",
            f"- Expected status: `{item.get('expected_status', '—')}`",
            f"- Actual status: `{item.get('actual_status', '—')}`",
            f"- Result: **{item.get('result', 'UNKNOWN')}**",
            "",
            "Response evidence:",
            "",
            "```json",
            json.dumps(item.get("response_body", item.get("reason", {})),
                       indent=2, ensure_ascii=False),
            "```",
            "",
        ])

    lines.extend(["## Limitations", ""])
    for limitation in report.get("limitations", []):
        lines.append(f"- {limitation}")

    lines.extend([
        "",
        "This report describes only the configured local lab tests. "
        "Passing the tests is not proof of overall API security.",
        "",
    ])

    return "\n".join(lines)


def make_html(report):
    summary = report.get("summary", {})
    results = report["results"]

    def esc(value):
        return html.escape(str(value))

    rows = []
    evidence = []

    for item in results:
        result = item.get("result", "UNKNOWN")
        status_class = (
            "pass" if result == "PASS"
            else "fail" if result == "FAIL"
            else "other"
        )
        actual = item.get("actual_status", item.get("status", "—"))

        rows.append(
            "<tr>"
            f"<td>{esc(item.get('test', ''))}</td>"
            f"<td><code>{esc(item.get('method', ''))} "
            f"{esc(item.get('path', ''))}</code></td>"
            f"<td>{esc(item.get('expected_status', '—'))}</td>"
            f"<td>{esc(actual)}</td>"
            f'<td><span class="badge {status_class}">'
            f"{esc(result)}</span></td>"
            "</tr>"
        )

        response = item.get(
            "response_body",
            item.get("reason", "No response evidence recorded"),
        )

        evidence.append(
            "<details>"
            f"<summary>{esc(item.get('test', 'Unnamed test'))}</summary>"
            "<dl>"
            f"<dt>Method</dt><dd>{esc(item.get('method', 'unknown'))}</dd>"
            f"<dt>Path</dt><dd>{esc(item.get('path', 'unknown'))}</dd>"
            f"<dt>Expected status</dt><dd>{esc(item.get('expected_status', '—'))}</dd>"
            f"<dt>Actual status</dt><dd>{esc(actual)}</dd>"
            f"<dt>Result</dt><dd>{esc(result)}</dd>"
            "</dl>"
            f"<pre>{esc(json.dumps(response, indent=2, ensure_ascii=False))}</pre>"
            "</details>"
        )

    limitations = "".join(
        f"<li>{esc(item)}</li>"
        for item in report.get("limitations", [])
    )

    generated = esc(report.get("generated_at", "unknown"))
    target = esc(report.get("target", "unknown"))
    version = esc(report.get("version", "unknown"))
    scope = esc(report.get("scope", "not specified"))

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>API Sentinel — Auth/BOLA Report</title>
<style>
:root {{
  color-scheme: dark;
  font-family: system-ui, -apple-system, sans-serif;
  background: #0b1020;
  color: #e5e7eb;
}}
body {{ max-width: 1050px; margin: 0 auto; padding: 24px; }}
header, section {{ background: #141b2d; border: 1px solid #29344b;
  border-radius: 14px; padding: 22px; margin-bottom: 18px; }}
h1 {{ margin-bottom: 6px; }}
.muted {{ color: #a6b0c3; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(140px,1fr));
  gap: 12px; }}
.card {{ background: #0b1020; border-radius: 10px; padding: 16px; }}
.number {{ font-size: 28px; font-weight: 700; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ padding: 12px 9px; text-align: left; border-bottom: 1px solid #29344b; }}
th {{ color: #a6b0c3; }}
.badge {{ display: inline-block; padding: 4px 9px; border-radius: 99px; font-weight: 700; }}
.pass {{ background: #123b2c; color: #86efac; }}
.fail {{ background: #4c1d1d; color: #fca5a5; }}
.other {{ background: #3b2e12; color: #fde68a; }}
code, pre {{ overflow-wrap: anywhere; }}
pre {{ white-space: pre-wrap; background: #0b1020; padding: 14px; border-radius: 8px; }}
details {{ border-top: 1px solid #29344b; padding: 14px 0; }}
summary {{ cursor: pointer; font-weight: 650; }}
dt {{ color: #a6b0c3; margin-top: 8px; }}
dd {{ margin-left: 0; }}
@media (max-width: 650px) {{
  body {{ padding: 12px; }}
  header, section {{ padding: 15px; overflow-wrap: anywhere; }}
  table {{ font-size: 13px; }}
  th, td {{ padding: 8px 5px; }}
}}
</style>
</head>
<body>
<header>
  <p class="muted">API SECURITY TESTING CONSOLE</p>
  <h1>API Sentinel</h1>
  <h2>Auth-Aware BOLA Assessment</h2>
  <p class="muted">Version {version} · Generated {generated}</p>
  <p>Scope: {scope}</p>
  <p>Target: <code>{target}</code></p>
</header>
<section>
  <h2>Summary</h2>
  <div class="cards">
    <div class="card"><div class="muted">Total tests</div>
      <div class="number">{summary.get('total', len(results))}</div></div>
    <div class="card"><div class="muted">Passed</div>
      <div class="number">{summary.get('pass', 0)}</div></div>
    <div class="card"><div class="muted">Failed</div>
      <div class="number">{summary.get('fail', 0)}</div></div>
    <div class="card"><div class="muted">Errors</div>
      <div class="number">{summary.get('error', 0)}</div></div>
  </div>
</section>
<section>
  <h2>Test results</h2>
  <div style="overflow-x:auto">
  <table>
    <thead><tr><th>Test</th><th>Endpoint</th><th>Expected</th>
    <th>Actual</th><th>Result</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  </div>
</section>
<section>
  <h2>Evidence details</h2>
  {''.join(evidence)}
</section>
<section>
  <h2>Limitations</h2>
  <ul>{limitations}</ul>
  <p class="muted">These results apply only to the configured local lab scenarios.
  They do not prove overall API security or assign a CVSS score.</p>
</section>
</body>
</html>
"""


def main():
    report = load_report()

    markdown = make_markdown(report)
    document = make_html(report)

    MD_OUT.write_text(markdown, encoding="utf-8")
    HTML_OUT.write_text(document, encoding="utf-8")

    print(f"Markdown report saved: {MD_OUT.relative_to(ROOT)}")
    print(f"HTML report saved: {HTML_OUT.relative_to(ROOT)}")
    print("CVSS: not assigned; manual risk assessment is required.")


if __name__ == "__main__":
    main()
