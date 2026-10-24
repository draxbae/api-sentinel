import json
from datetime import datetime, timezone
from pathlib import Path


SOURCE = Path("reports/bola_comparison_v0.6.0.json")
OUTPUT = Path("reports/security_report_v0.7.0.json")


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Source report not found: {SOURCE}")

    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    findings = []

    for target in data.get("reports", []):
        for result in target.get("results", []):
            if result.get("result") != "FINDING":
                continue

            findings.append({
                "title": "Potential Broken Object Level Authorization",
                "category": "BOLA / IDOR",
                "severity": "High",
                "target": target.get("base_url"),
                "test": result.get("test"),
                "object_id": result.get("order_id"),
                "http_status": result.get("actual_status"),
                "evidence": result.get("detail"),
                "recommendation": (
                    "Enforce server-side object ownership checks for every "
                    "request. Verify that the authenticated principal is "
                    "authorized to access the requested object."
                ),
                "scope": "Local lab fixture; validate before generalizing.",
            })

    report = {
        "tool": "API Sentinel",
        "version": "0.7.0",
        "report_type": "Security assessment summary",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_report": str(SOURCE),
        "summary": {
            "targets_tested": len(data.get("reports", [])),
            "findings": len(findings),
            "note": (
                "Severity is a preliminary lab classification, not a "
                "production risk rating."
            ),
        },
        "findings": findings,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Report saved: {OUTPUT}")
    print(f"Findings: {len(findings)}")


if __name__ == "__main__":
    main()
