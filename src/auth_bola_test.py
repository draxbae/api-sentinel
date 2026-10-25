#!/usr/bin/env python3
"""API Sentinel v1.1.0 — authenticated BOLA tests for localhost lab."""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import httpx


def validate_target(raw_url):
    parsed = urlsplit(raw_url)

    try:
        port = parsed.port
    except ValueError:
        raise SystemExit("Invalid target port.")

    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"127.0.0.1", "localhost"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
    ):
        raise SystemExit("Only a plain HTTP localhost base URL is allowed.")

    if port is not None and not 1 <= port <= 65535:
        raise SystemExit("Invalid target port.")

    return raw_url.rstrip("/")


def request_case(client, base_url, name, order_id, token, expected_status):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"{base_url}/orders/{order_id}"

    try:
        response = client.get(url, headers=headers)
        passed = response.status_code == expected_status

        try:
            body = response.json()
        except ValueError:
            body = {"body_preview": response.text[:300]}

        # Record only safe response evidence; never store authorization tokens.
        result = {
            "test": name,
            "method": "GET",
            "path": f"/orders/{order_id}",
            "expected_status": expected_status,
            "actual_status": response.status_code,
            "result": "PASS" if passed else "FAIL",
            "response_body": body,
        }
        return result

    except httpx.HTTPError as exc:
        return {
            "test": name,
            "method": "GET",
            "path": f"/orders/{order_id}",
            "expected_status": expected_status,
            "result": "ERROR",
            "reason": str(exc),
        }


def main():
    raw_url = os.environ.get(
        "API_SENTINEL_BASE_URL", "http://127.0.0.1:8000"
    )
    base_url = validate_target(raw_url)

    # These are lab tokens, not production credentials.
    alice_token = os.environ.get("API_SENTINEL_ALICE_TOKEN", "alice-token")
    bob_token = os.environ.get("API_SENTINEL_BOB_TOKEN", "bob-token")

    if not re.fullmatch(r"[A-Za-z0-9._~-]{1,256}", alice_token):
        raise SystemExit("Invalid lab token format for Alice.")
    if not re.fullmatch(r"[A-Za-z0-9._~-]{1,256}", bob_token):
        raise SystemExit("Invalid lab token format for Bob.")
    if alice_token == bob_token:
        raise SystemExit("Alice and Bob must use different lab tokens.")

    cases = [
        ("Alice reads own order", "1001", alice_token, 200),
        ("Alice reads Bob's order", "1002", alice_token, 403),
        ("Bob reads own order", "1002", bob_token, 200),
        ("Unauthenticated request", "1001", None, 401),
        ("Invalid token", "1001", "invalid-lab-token", 401),
        ("Nonexistent order", "999999", alice_token, 404),
    ]

    results = []

    with httpx.Client(
        timeout=5.0,
        follow_redirects=False,
        trust_env=False,
    ) as client:
        for name, order_id, token, expected in cases:
            result = request_case(
                client, base_url, name, order_id, token, expected
            )
            results.append(result)

            status = result.get("actual_status", result.get("result"))
            print(f"[{result['result']}] {name} — {status}")

    passed = sum(r["result"] == "PASS" for r in results)
    failed = sum(r["result"] == "FAIL" for r in results)
    errors = sum(r["result"] == "ERROR" for r in results)

    report = {
        "tool": "API Sentinel",
        "version": "1.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "localhost lab only",
        "target": base_url,
        "summary": {
            "total": len(results),
            "pass": passed,
            "fail": failed,
            "error": errors,
        },
        "results": results,
        "limitations": [
            "Only predefined local lab cases were tested.",
            "Passing these tests does not prove overall API security.",
            "This report does not assign a CVSS score.",
        ],
    }

    output = Path("reports/auth_bola_report.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"\nSummary: {passed}/{len(results)} passed; {failed} failed; {errors} errors")
    print(f"Report: {output}")


if __name__ == "__main__":
    main()
