import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx


def check_endpoint(base_url: str, endpoint: dict) -> dict:
    method = endpoint["method"].upper()
    path = endpoint["path"]

    # Hindari endpoint yang membutuhkan parameter path dinamis
    if "{" in path or "}" in path:
        return {
            "method": method,
            "path": path,
            "status": "SKIPPED",
            "reason": "Dynamic path parameter needs a test value",
        }

    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    try:
        with httpx.Client(
            timeout=10.0,
            follow_redirects=False,
        ) as client:
            response = client.request(method, url)

        return {
            "method": method,
            "path": path,
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type"),
        }

    except httpx.HTTPError as exc:
        return {
            "method": method,
            "path": path,
            "status": "ERROR",
            "reason": str(exc),
        }


def main():
    base_url = os.environ.get("API_SENTINEL_BASE_URL")

    if not base_url:
        raise SystemExit(
            "Set API_SENTINEL_BASE_URL to an API lab you are authorized to test."
        )

    # Hanya menerima alamat localhost untuk tahap latihan ini.
    if not base_url.startswith(("http://127.0.0.1", "http://localhost", "http://[::1]")):
        raise SystemExit("For this version, use a localhost lab target only.")

    from openapi_parser import load_openapi, map_endpoints

    spec = load_openapi("examples/openapi.yaml")
    endpoints = map_endpoints(spec)
    results = [check_endpoint(base_url, item) for item in endpoints]

    report = {
        "tool": "API Sentinel",
        "version": "0.3.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "results": results,
    }

    output = Path("reports/http_check.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Checked: {len(results)} endpoints")
    print(f"Report: {output}")


if __name__ == "__main__":
    main()
