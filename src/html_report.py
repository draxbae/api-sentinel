
import html
import json
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path("reports/bola_comparison_v0.8.0.json")
OUTPUT = Path("reports/security_report_v0.8.0.html")


def esc(value):
    return html.escape(str(value if value is not None else "N/A"))


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Source report tidak ditemukan: {SOURCE}")

    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    targets = data.get("reports", [])
    findings = [
        (target, result)
        for target in targets
        for result in target.get("results", [])
        if result.get("result") == "FINDING"
    ]

    total_tests = sum(t.get("total_tests", 0) for t in targets)

    rows = []
    for target in targets:
        for result in target.get("results", []):
            status = result.get("result", "UNKNOWN")
            rows.append(
                "<tr>"
                f"<td>{esc(target.get('target'))}</td>"
                f"<td>{esc(result.get('test'))}</td>"
                f"<td>{esc(result.get('expected_status'))}</td>"
                f"<td>{esc(result.get('actual_status'))}</td>"
                f"<td><strong>{esc(status)}</strong></td>"
                "</tr>"
            )

    finding_sections = []
    for target, result in findings:
        finding_sections.append(f"""
        <section class="finding">
          <h3>Potential BOLA / IDOR</h3>
          <p><b>Target lab:</b> {esc(target.get('base_url'))}</p>
          <p><b>Test:</b> {esc(result.get('test'))}</p>
          <p><b>Object ID:</b> {esc(result.get('order_id'))}</p>
          <p><b>Expected HTTP:</b> {esc(result.get('expected_status'))}</p>
          <p><b>Actual HTTP:</b> {esc(result.get('actual_status'))}</p>
          <p><b>Evidence:</b> {esc(result.get('detail'))}</p>
          <p><b>Recommendation:</b> Enforce server-side ownership and
          authorization checks for every requested object.</p>
        </section>
        """)

    if not finding_sections:
        finding_sections = [
            "<p>No results marked FINDING in the source report.</p>"
        ]

    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>API Sentinel Security Report</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 1000px;
       margin: 36px auto; padding: 0 18px; color: #202938; }}
header, .card, .finding {{ border: 1px solid #d8dee8; border-radius: 12px;
                           padding: 18px; margin-bottom: 18px; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit,
         minmax(150px, 1fr)); gap: 12px; }}
.metric {{ font-size: 2rem; font-weight: 700; }}
table {{ width: 100%; border-collapse: collapse; display: block;
         overflow-x: auto; }}
th, td {{ text-align: left; border-bottom: 1px solid #e2e6ed;
          padding: 10px; }}
th {{ background: #f3f5f8; }}
.finding {{ border-left: 5px solid #d97706; overflow-wrap: anywhere; }}
.note {{ color: #566174; }}
</style>
</head>
<body>
<header>
  <h1>API Sentinel</h1>
  <p>Security Assessment Report · Version 0.8.0</p>
  <p>Generated: {esc(datetime.now(timezone.utc).isoformat())}</p>
  <p class="note">Scope: local BOLA/IDOR fixtures only.</p>
</header>
<div class="cards">
  <div class="card"><div>Targets tested</div>
  <div class="metric">{len(targets)}</div></div>
  <div class="card"><div>Tests</div>
  <div class="metric">{total_tests}</div></div>
  <div class="card"><div>Potential findings</div>
  <div class="metric">{len(findings)}</div></div>
</div>
<h2>Test results</h2>
<div class="card">
<table>
<thead><tr><th>Target</th><th>Test</th><th>Expected</th>
<th>Actual</th><th>Result</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</div>
<h2>Findings and recommendations</h2>
{''.join(finding_sections)}
<h2>Limitations</h2>
<p class="note">This assessment uses intentionally configured local fixtures.
The lab result is not proof of a vulnerability in a production system.
Further authorized validation is required before assigning a real-world risk.</p>
<p class="note">Source: {esc(SOURCE)}</p>
</body>
</html>
"""

    OUTPUT.write_text(document, encoding="utf-8")
    print(f"HTML report saved: {OUTPUT}")
    print(f"Potential findings: {len(findings)}")


if __name__ == "__main__":
    main()
