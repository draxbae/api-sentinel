
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

TARGETS = [
    {
        "name": "secure",
        "url": "http://127.0.0.1:8000",
        "expected_cross_owner": 403,
    },
    {
        "name": "vulnerable_lab",
        "url": "http://127.0.0.1:8001",
        "expected_cross_owner": 403,
    },
]


def check_target(target):
    base_url = target["url"]
    results = []

    cases = [
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
    ]

    with httpx.Client(timeout=5.0) as client:
        for case in cases:
            headers = {}
            if case["token"]:
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

                if case["name"] == "Alice reads Bob's order":
                    if status == 200 and item == "Keyboard":
                        result = "FINDING"
                        detail = (
                            "Alice received Bob's order data: "
                            "potential BOLA in local lab."
                        )
                    elif status == 403:
                        result = "PASS"
                        detail = "Cross-owner access was denied."
                    else:
                        result = "REVIEW"
                        detail = "Unexpected cross-owner response."
                else:
                    ok = status == case["expected_status"]
                    if case["expected_item"] is not None:
                        ok = ok and item == case["expected_item"]

                    result = "PASS" if ok else "FAIL"
                    detail = (
                        "Response matched expectation."
                        if ok else "Response differed from expectation."
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
            print(f"[{target['name']}] [{entry['result']}] {entry['test']}")

    return {
        "target": target["name"],
        "base_url": base_url,
        "total_tests": len(results),
        "counts": {
            status: sum(r["result"] == status for r in results)
            for status in ("PASS", "FINDING", "FAIL", "REVIEW", "ERROR")
        },
        "results": results,
    }


def main():
    reports = [check_target(target) for target in TARGETS]

    report = {
        "tool": "API Sentinel",
        "version": "0.6.0",
        "test_type": "Local BOLA/IDOR comparison lab",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reports": reports,
        "note": (
            "Only local fixtures are tested. FINDING indicates potential "
            "cross-owner data exposure in this lab, not a universal verdict."
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
