
import json
import sys
from pathlib import Path

REPORT = Path("reports/bola_comparison.json")


def main():
    if not REPORT.exists():
        print(f"FAIL: Report tidak ditemukan: {REPORT}")
        sys.exit(1)

    data = json.loads(REPORT.read_text(encoding="utf-8"))
    targets = data.get("reports", [])
    checks = []

    for target in targets:
        url = target.get("base_url", "")
        results = target.get("results", [])

        cross_owner = next(
            (
                r for r in results
                if "Alice reads Bob" in r.get("test", "")
            ),
            None,
        )
        unauth = next(
            (
                r for r in results
                if "Unauthenticated" in r.get("test", "")
            ),
            None,
        )

        if url.endswith(":8000"):
            checks.append((
                "Secure API blocks cross-owner access",
                cross_owner is not None
                and cross_owner.get("result") == "PASS"
                and cross_owner.get("actual_status") == 403,
            ))
        elif url.endswith(":8001"):
            checks.append((
                "Vulnerable lab detects BOLA",
                cross_owner is not None
                and cross_owner.get("result") == "FINDING"
                and cross_owner.get("actual_status") == 200,
            ))
        else:
            continue

        checks.append((
            f"Unauthenticated access rejected ({url})",
            unauth is not None
            and unauth.get("actual_status") == 401,
        ))

    for name, passed in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")

    if len(checks) != 4 or not all(ok for _, ok in checks):
        print("FAIL: Regression test belum seluruhnya lulus.")
        sys.exit(1)

    print("\nPASS: Semua regression test berhasil.")


if __name__ == "__main__":
    main()
