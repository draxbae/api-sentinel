#!/usr/bin/env python3

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit

import httpx


def validate_local_url(base_url: str) -> str:
    """Allow HTTP requests only to explicit localhost addresses."""
    try:
        parsed = urlsplit(base_url)
        hostname = (parsed.hostname or "").lower()
        port = parsed.port
    except ValueError as exc:
        raise SystemExit(f"Invalid URL: {exc}")

    if (
        parsed.scheme != "http"
        or hostname not in {"127.0.0.1", "localhost", "::1"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise SystemExit(
            "Target rejected. Use an HTTP localhost lab URL only."
        )

    if port is not None and not 1 <= port <= 65535:
        raise SystemExit("Invalid port.")

    if parsed.path not in ("", "/"):
        raise SystemExit("Provide only the base URL, without a path.")

    return f"http://{hostname}" + (f":{port}" if port else "")


def resolve_path(path: str) -> tuple[str | None, str | None]:
    """
    Resolve explicitly supported path parameters for the local lab.
    Unknown parameters are skipped instead of guessed.
    """
    order_id = os.environ.get("API_SENTINEL_ORDER_ID", "1001")

    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", order_id):
        return None, "Invalid API_SENTINEL_ORDER_ID value"

    matches = re.findall(r"\{([^{}]+)\}", path)

    if not matches:
        if "{" in path or "}" in path:
            return None, "Malformed path parameter"
        return path, None

    resolved = path

    for name in matches:
        if name != "order_id":
            return None, f"No test value configured for parameter: {name}"

        resolved = resolved.replace(
            "{order_id}",
            quote(order_id, safe=""),
        )

    if "{" in resolved or "}" in resolved:
        return None, "Unresolved path parameter"

    return resolved, None


def check_endpoint(client: httpx.Client, base_url: str, endpoint: dict) -> dict:
    method = endpoint["method"].upper()
    path = endpoint["path"]

    # This checker performs read-only HTTP checks.
    if method not in {"GET", "HEAD"}:
        return {
            "method": method,
            "path": path,
            "status": "SKIPPED",
            "reason": "Only GET and HEAD are allowed by this checker",
        }

    resolved_path, reason = resolve_path(path)

    if resolved_path is None:
        return {
            "method": method,
            "path": path,
            "status": "SKIPPED",
            "reason": reason,
        }

    url = f"{base_url.rstrip('/')}/{resolved_path.lstrip('/')}"

    try:
        response = client.request(method, url)

        result = {
            "method": method,
            "path": path,
            "resolved_path": resolved_path,
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type"),
        }

        if 300 <= response.status_code < 400:
            result["note"] = "Redirect not followed"

        return result

    except httpx.HTTPError as exc:
        return {
            "method": method,
            "path": path,
            "resolved_path": resolved_path,
            "status": "ERROR",
            "reason": str(exc),
        }


def main():
    supplied_url = os.environ.get("API_SENTINEL_BASE_URL")

    if not supplied_url:
        raise SystemExit(
            "Set API_SENTINEL_BASE_URL to your authorized localhost lab."
        )

    base_url = validate_local_url(supplied_url)

    from openapi_parser import load_openapi, map_endpoints

    spec = load_openapi("examples/openapi.yaml")
    endpoints = map_endpoints(spec)

    results = []

    try:
        with httpx.Client(
            timeout=10.0,
            follow_redirects=False,
            trust_env=False,
        ) as client:
            for endpoint in endpoints:
                results.append(
                    check_endpoint(client, base_url, endpoint)
                )
    except httpx.HTTPError as exc:
        raise SystemExit(f"Could not initialize HTTP client: {exc}")

    report = {
        "tool": "API Sentinel",
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "scope": "localhost lab only",
        "dynamic_parameter_values": {
            "order_id": os.environ.get("API_SENTINEL_ORDER_ID", "1001")
        },
        "results": results,
    }

    output = Path("reports/http_check.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Checked: {len(results)} endpoints")
    print(f"Report: {output}")

    for result in results:
        status = result.get("status_code", result.get("status", "UNKNOWN"))
        print(f"[{status}] {result['method']} {result['path']}")


if __name__ == "__main__":
    main()
