import json
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path("reports/bola_comparison.json")
OUTPUT = Path("reports/security_report_v1.0.0.md")


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Source report tidak ditemukan: {SOURCE}")

    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    targets = data.get("reports", [])

    findings = [
        (target, result)
        for target in targets
        for result in target.get("results", [])
        if result.get("result") == "FINDING"
    ]

    total_tests = sum(t.get("total_tests", 0) for t in targets)

    lines = [
        "# API Sentinel — Security Assessment",
        "",
        "**Versi:** 1.0.0",
        f"**Dibuat:** {datetime.now(timezone.utc).isoformat()}",
        "**Cakupan:** Lab BOLA/IDOR lokal",
        "",
        "## Ringkasan",
        "",
        f"- Target lab diuji: {len(targets)}",
        f"- Total pengujian: {total_tests}",
        f"- Temuan potensial: {len(findings)}",
        "",
        "| Target lab | Pengujian | PASS | FINDING |",
        "|---|---:|---:|---:|",
    ]

    for target in targets:
        counts = target.get("counts", {})
        lines.append(
            f"| {target.get('target', 'unknown')} "
            f"| {target.get('total_tests', 0)} "
            f"| {counts.get('PASS', 0)} "
            f"| {counts.get('FINDING', 0)} |"
        )

    lines.extend(["", "## Temuan", ""])

    if not findings:
        lines.append("Tidak ada temuan berstatus FINDING pada laporan sumber.")
    else:
        for index, (target, result) in enumerate(findings, start=1):
            evidence = result.get("evidence") or {}
            response_body = evidence.get("response_body")

            lines.extend([
                f"### {index}. Potensi BOLA / IDOR",
                "",
                f"- **Target lab:** `{target.get('base_url', 'unknown')}`",
                f"- **Pengujian:** {result.get('test', 'N/A')}",
                f"- **Metode:** `{result.get('method', 'N/A')}`",
                f"- **Endpoint:** `{result.get('endpoint', 'N/A')}`",
                f"- **ID objek:** `{result.get('order_id', 'N/A')}`",
                f"- **Status HTTP yang diharapkan:** "
                f"`{result.get('expected_status', 'N/A')}`",
                f"- **Status HTTP aktual:** "
                f"`{result.get('actual_status', 'N/A')}`",
                f"- **Hasil lintas pemilik:** "
                f"`{evidence.get('cross_owner_access', 'N/A')}`",
                f"- **Data terekspos:** "
                f"`{evidence.get('data_exposed', 'N/A')}`",
                f"- **Detail:** {result.get('detail', 'N/A')}",
                "",
                "**Response body:**",
                "",
                "```json",
                json.dumps(
                    response_body,
                    indent=2,
                    ensure_ascii=False,
                ) if response_body is not None else "Tidak tersedia",
                "```",
                "",
                "**Rekomendasi:** Terapkan pemeriksaan otorisasi di sisi server "
                "untuk setiap objek dan pastikan pengguna yang terautentikasi "
                "memiliki izin mengakses objek yang diminta.",
                "",
            ])

    lines.extend([
        "## Batasan",
        "",
        "Pengujian ini hanya menggunakan fixture lokal yang sengaja dibuat "
        "untuk demonstrasi. Temuan bukan bukti kerentanan pada sistem produksi. "
        "Validasi tambahan diperlukan sebelum menentukan tingkat risiko nyata.",
        "",
        f"**Sumber:** `{SOURCE}`",
    ])

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Markdown report saved: {OUTPUT}")
    print(f"Potential findings: {len(findings)}")


if __name__ == "__main__":
    main()
