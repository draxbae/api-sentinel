import json
import sys
from pathlib import Path

REPORT = Path("reports/bola_comparison.json")

EXPECTED = {
    "Alice reads own order": 200,
    "Alice reads Bob's order": 403,
    "Bob reads own order": 200,
    "Unauthenticated request": 401,
    "Invalid token": 401,
    "Nonexistent order": 404,
}

checks = []


def check(label, condition):
    checks.append((label, bool(condition)))


def main():
    if not REPORT.exists():
        print(f"[FAIL] Report tidak ditemukan: {REPORT}")
        return 1

    try:
        data = json.loads(REPORT.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] Gagal membaca report: {exc}")
        return 1

    check("Report version 1.0.0", data.get("version") == "1.0.0")

    reports = {
        entry.get("target"): entry
        for entry in data.get("reports", [])
    }

    for target in ("secure", "vulnerable_lab"):
        check(f"Target {target} tersedia", target in reports)

        if target not in reports:
            continue

        results = reports[target].get("results", [])
        by_name = {item.get("test"): item for item in results}

        check(
            f"{target}: enam kasus unik",
            len(results) == 6
            and len(by_name) == 6
            and set(by_name) == set(EXPECTED),
        )

        for name, expected_status in EXPECTED.items():
            item = by_name.get(name)
            if item is None:
                continue

            expected = item.get("expected_status")
            actual = item.get("actual_status")
            outcome = item.get("result")

            if target == "vulnerable_lab" and name == "Alice reads Bob's order":
                passed = (
                    expected == 403
                    and actual == 200
                    and outcome == "FINDING"
                )
                label = "Lab mendeteksi BOLA yang disengaja"
            else:
                passed = (
                    expected == expected_status
                    and actual == expected_status
                    and outcome == "PASS"
                )
                label = f"{target}: {name}"

            check(label, passed)

        if target == "secure":
            check(
                "Secure API: semua kasus PASS",
                all(item.get("result") == "PASS" for item in results),
            )

        if target == "vulnerable_lab":
            check(
                "Lab: tepat satu FINDING",
                sum(item.get("result") == "FINDING" for item in results) == 1,
            )

    for label, passed in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {label}")

    failed = sum(not passed for _, passed in checks)
    print(f"\nHasil: {len(checks) - failed}/{len(checks)} pemeriksaan lulus.")

    if failed:
        print("FAIL: Masih ada pemeriksaan yang gagal.")
        return 1

    print("PASS: Semua regression test lulus.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
