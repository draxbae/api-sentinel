
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

TARGETS = [
    {
        "name": "secure",
        "url": "http://127.0.0.1:8000",
    },
    {
        "name": "vulnerable_lab",
        "url": "http://127.0.0.1:8001",
    },
]

CASES = [
    {
        "name": "Alice reads own order",
        "token": "alice-token",
        "order_id": "1001",
        "expected_status": 200,
        "expected_item": "Laptop",
    },
    {
        "name": "Alice reads Bob's order",
        "token": "alice-token",
        "order_id": "1002",
        "expected_status": 403,
        "expected_item": None,
        "cross_owner": True,
    },
    {
        "name": "Bob reads own order",
        "token": "bob-token",
        "order_id": "1002",
        "expected_status": 200,
        "expected_item": "Keyboard",
    },
    {
        "name": "Unauthenticated request",
        "token": None,
        "order_id": "1001",
        "expected_status": 401,
        "expected_item": None,
    },
    {
        "name": "Invalid token",
        "token": "invalid-token",
        "order_id": "1001",
        "expected_status": 401,
        "expected_item": None,
    },
    {
        "name": "Nonexistent order",
        "token": "alice-token",
        "order_id": "9999",
        "expected_status": 404,
        "expected_item": None,
    },
]


def check_target(target):
    base_url = target["url"]
    results = []

    with httpx.Client(timeout=5.0) as client:
        for case in CASES:
            headers = {}
            if case["token"] is not None:
                headers["Authorization"] = f"Bearer {case['token']}"

            try:
                response = client.get(
                    f"{base_url}/orders/{case['order_id']}",
                    headers=headers,
                )
                status = response.status_code

                try:
                    body = response.json()
                except ValueError:
                    body = {}

                item = body.get("item")

                if case.get("cross_owner"):
                    if status == 200 and item == "Keyboard":
                        result = (
                            "FINDING"
                            if target["name"] == "vulnerable_lab"
                            else "FAIL"
                        )
                        detail = (
                            "Cross-owner data was exposed."
                            if result == "FINDING"
                            else "Secure API exposed another user's data."
                        )
                    elif status == 403:
                        result = (
                            "PASS"
                            if target["name"] == "secure"
                            else "REVIEW"
                        )
                        detail = (
                            "Cross-owner access was denied."
                            if result == "PASS"
                            else "Lab behavior changed; investigate fixture."
                        )
                    else:
                        result = "FAIL"
                        detail = "Unexpected cross-owner response."
                else:
                    ok = status == case["expected_status"]
                    if case["expected_item"] is not None:
                        ok = ok and item == case["expected_item"]

                    result = "PASS" if ok else "FAIL"
                    detail = (
                        "Response matched expectation."
                        if ok
                        else (
                            f"Expected HTTP {case['expected_status']}; "
                            f"received HTTP {status}."
                        )
                    )

                entry = {
                    "test": case["name"],
                    "order_id": case["order_id"],
                    "expected_status": case["expected_status"],
                    "actual_status": status,
                    "result": result,
                    "detail": detail,
                }

            except httpx.HTTPError as exc:
                entry = {
                    "test": case["name"],
                    "order_id": case["order_id"],
                    "expected_status": case["expected_status"],
                    "actual_status": None,
                    "result": "ERROR",
                    "detail": str(exc),
                }

            results.append(entry)
            print(
                f"[{target['name']}] "
                f"[{entry['result']}] {entry['test']}"
            )

    statuses = ("PASS", "FINDING", "FAIL", "REVIEW", "ERROR")

    return {
        "target": target["name"],
        "base_url": base_url,
        "total_tests": len(results),
        "counts": {
            status: sum(r["result"] == status for r in results)
            for status in statuses
        },
        "results": results,
    }


def main():
    reports = [check_target(target) for target in TARGETS]

    report = {
        "tool": "API Sentinel",
        "version": "1.0.0",
        "test_type": "Local BOLA/IDOR comparison lab",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reports": reports,
        "note": (
            "Only local fixtures are tested. FINDING indicates potential "
            "cross-owner data exposure in the intentionally vulnerable "
            "local lab; it does not establish a production vulnerability."
        ),
    }

    output = Path("reports/bola_comparison.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"\nReport saved: {output}")


if __name__ == "__main__":
    main()
