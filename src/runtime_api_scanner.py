#!/usr/bin/env python3

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import httpx

from openapi_parser import load_openapi, map_endpoints


ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"

ALLOWED_METHODS = {"GET", "HEAD"}

SECURITY_HEADERS = (
    "x-content-type-options",
    "content-security-policy",
    "strict-transport-security",
    "cache-control",
)


def validate_base_url(value: str) -> str:
    parsed = urlsplit(value)

    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ValueError(
            "Base URL harus berupa origin HTTP(S), "
            "misalnya https://petstore3.swagger.io"
        )

    try:
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("Port pada base URL tidak valid") from exc

    return f"{parsed.scheme}://{parsed.netloc}"


def resolve_server(spec: dict, origin: str) -> str:
    servers = spec.get("servers") or [{"url": "/"}]
    server_url = servers[0].get("url", "/")

    if "{" in server_url or "}" in server_url:
        raise ValueError(
            "Server URL memiliki variable yang belum didukung."
        )

    parsed_server = urlsplit(server_url)

    if parsed_server.scheme:
        server_origin = validate_base_url(
            f"{parsed_server.scheme}://{parsed_server.netloc}"
        )

        if server_origin != origin:
            raise ValueError(
                "Server eksternal berbeda dari origin yang dipilih. "
                "Pilih origin server yang sesuai."
            )

        return server_origin + parsed_server.path.rstrip("/")

    return origin + "/" + server_url.lstrip("/").rstrip("/")


def inspect_headers(headers) -> list[str]:
    present = {key.lower() for key in headers.keys()}
    missing = []

    for name in SECURITY_HEADERS:
        if name not in present:
            missing.append(name)

    return missing


def build_safe_query(path: str, method: str):
    """Use only explicit, approved query values for demo endpoints."""
    if method.upper() != "GET":
        return {}

    if path == "/pet/findByStatus":
        return {"status": "available"}

    if path == "/pet/findByTags":
        return None

    return {}


def scan_endpoint(
    client: httpx.Client,
    server_url: str,
    endpoint: dict,
) -> dict:
    method = endpoint["method"].upper()
    path = endpoint["path"]

    base_result = {
        "method": method,
        "path": path,
        "summary": endpoint.get("summary"),
    }

    if path in {"/user/login", "/user/logout"}:
        return {
            **base_result,
            "status": "SKIPPED",
            "reason": "Authentication/session endpoint excluded by default.",
        }

    if method not in ALLOWED_METHODS:
        return {
            **base_result,
            "status": "SKIPPED",
            "reason": "Runtime scanner hanya mengizinkan GET dan HEAD.",
        }

    if "{" in path or "}" in path:
        return {
            **base_result,
            "status": "SKIPPED",
            "reason": "Path membutuhkan parameter; nilai tidak ditebak.",
        }

    url = urljoin(server_url.rstrip("/") + "/", path.lstrip("/"))
    started = time.monotonic()

    try:
        query = build_safe_query(path, method)

        if query is None:
            return {
                **base_result,
                "status": "SKIPPED",
                "reason": "Required query parameter has no approved test value.",
            }

        response = client.request(method, url, params=query)
        elapsed_ms = round((time.monotonic() - started) * 1000, 2)

        result = {
            **base_result,
            "url": url,
            "http_status": response.status_code,
            "elapsed_ms": elapsed_ms,
            "content_type": response.headers.get("content-type"),
            "missing_headers_for_review": inspect_headers(
                response.headers
            ),
            "redirect_followed": False,
        }

        content_type = response.headers.get("content-type", "").lower()

        if method == "HEAD":
            result["json_check"] = "NOT_APPLICABLE"
        elif "json" in content_type:
            try:
                response.json()
                result["json_check"] = "VALID"
            except ValueError:
                result["json_check"] = "INVALID"
        else:
            result["json_check"] = "NOT_JSON_CONTENT_TYPE"

        if 300 <= response.status_code < 400:
            result["note"] = "Redirect tidak diikuti."

        return result

    except httpx.HTTPError as exc:
        return {
            **base_result,
            "url": url,
            "status": "ERROR",
            "reason": str(exc),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Read-only runtime checks for an OpenAPI target."
    )
    parser.add_argument("spec_path", help="Path ke OpenAPI JSON/YAML")
    parser.add_argument(
        "--origin",
        required=True,
        help="Origin target yang diizinkan, misalnya https://example.com",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Jeda minimal antar-request dalam detik (default 0.5)",
    )
    args = parser.parse_args()

    if args.delay < 0.5:
        parser.error("Delay minimum adalah 0.5 detik.")

    try:
        spec = load_openapi(args.spec_path)
        origin = validate_base_url(args.origin)
        server_url = resolve_server(spec, origin)
        endpoints = map_endpoints(spec)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    results = []

    REPORTS.mkdir(exist_ok=True)

    try:
        with httpx.Client(
            timeout=10.0,
            follow_redirects=False,
            trust_env=False,
            headers={"User-Agent": "API-Sentinel/1.0.0"},
        ) as client:
            for index, endpoint in enumerate(endpoints):
                if index and endpoint["method"].upper() in ALLOWED_METHODS:
                    time.sleep(args.delay)

                results.append(
                    scan_endpoint(client, server_url, endpoint)
                )
    except KeyboardInterrupt:
        print("\nScan dihentikan oleh pengguna.")

    report = {
        "tool": "API Sentinel",
        "feature": "Runtime API Scanner",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "specification": str(Path(args.spec_path)),
        "server_url": server_url,
        "scope": "Read-only GET/HEAD checks",
        "results": results,
    }

    output = REPORTS / "runtime_api_scan.json"
    output.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\n=== API SENTINEL RUNTIME SCAN ===")
    print(f"Server: {server_url}")
    print(f"Endpoint dalam spesifikasi: {len(endpoints)}")
    print(f"Laporan: {output}")

    for result in results:
        status = result.get(
            "http_status",
            result.get("status", "UNKNOWN"),
        )
        print(f"[{status}] {result['method']} {result['path']}")


if __name__ == "__main__":
    main()
