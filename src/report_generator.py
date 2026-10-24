import json
from datetime import datetime, timezone
from pathlib import Path


def save_json_report(findings: list[dict], output_path: str) -> None:
    report = {
        "tool": "API Sentinel",
        "version": "0.2.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_findings": len(findings),
        "findings": findings,
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"[+] Report saved: {output}")
    print(f"[+] Total findings: {len(findings)}")


if __name__ == "__main__":
    from openapi_parser import load_openapi
    from spec_audit import audit_spec

    spec = load_openapi("examples/openapi.yaml")
    findings = audit_spec(spec)
    save_json_report(findings, "reports/spec_audit.json")
