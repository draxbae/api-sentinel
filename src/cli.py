
#!/usr/bin/env python3
"""
API SENTINEL
API Security Testing Console

Menu interaktif untuk menjalankan modul keamanan API.
Pengujian dibatasi pada lab lokal untuk scanner HTTP.
"""

import os
import sys
import time
import shutil
import socket
import subprocess
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
REPORTS = ROOT / "reports"
BACKUPS = ROOT / "backups"

REPORTS.mkdir(exist_ok=True)
BACKUPS.mkdir(exist_ok=True)

PYTHON = sys.executable

# ANSI colors
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
DIM = "\033[2m"


# ============================================================
# TERMINAL HELPERS
# ============================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input(f"\n{DIM}Tekan ENTER untuk kembali ke menu...{RESET}")


def line():
    print(f"{CYAN}{'─' * 58}{RESET}")


def heading(title):
    print()
    line()
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    line()


def print_status(label, message, color=CYAN):
    print(f"  {color}[{label}]{RESET} {message}")


def port_is_open(host, port):
    """Check whether a TCP port is accepting connections."""
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def run_script(script_name, extra_args=None, env=None):
    """Run an existing project module without changing its source."""
    script_path = SRC / script_name

    if not script_path.is_file():
        print_status("ERROR", f"File tidak ditemukan: {script_path}", RED)
        return False

    command = [PYTHON, str(script_path)]

    if extra_args:
        command.extend(extra_args)

    print_status("RUN", " ".join(command), BLUE)

    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            check=False,
        )
        if result.returncode == 0:
            print_status("OK", f"{script_name} selesai.", GREEN)
            return True

        print_status(
            "ERROR",
            f"{script_name} keluar dengan kode {result.returncode}.",
            RED,
        )
        return False

    except KeyboardInterrupt:
        print_status("STOP", "Proses dihentikan oleh pengguna.", YELLOW)
        return False
    except OSError as exc:
        print_status("ERROR", str(exc), RED)
        return False


# ============================================================
# LOGO / BANNER
# ============================================================

def show_banner():
    clear_screen()

    print(f"{CYAN}{BOLD}")
    print(r"""
     _    ____ ___   ____  _______   __
    / \  |  _ \_ _| / ___|| ____\ \ / /
   / _ \ | |_) | |  \___ \|  _|  \ V /
  / ___ \|  __/| |   ___) | |___  | |
 /_/   \_\_|  |___| |____/|_____| |_|

             .-----------------.
             |   /---------\   |
             |  |  (o) (o) |   |
             |  |     ^     |  |
             |  |   \___/    |  |
             |   \_________/   |
             '--------+--------'
""")
    print(f"{RESET}{BOLD}             API SENTINEL{RESET}")
    print(f"{CYAN}       API Security Testing Console{RESET}")
    print(f"{DIM}        Guarding Every API Request{RESET}")
    print()


# ============================================================
# MENU
# ============================================================

def show_menu():
    print(f"  {CYAN}[1]{RESET} BOLA / IDOR Scanner (local lab)")
    print(f"  {CYAN}[2]{RESET} OpenAPI Specification Audit")
    print(f"  {CYAN}[3]{RESET} HTTP Security Checks (localhost only)")
    print(f"  {CYAN}[4]{RESET} View Reports")
    print(f"  {CYAN}[5]{RESET} Generate HTML and Markdown Reports")
    print(f"  {CYAN}[6]{RESET} Exit")
    print(f"  {CYAN}[7]{RESET} Auth-Aware BOLA Tests")
    print(f"  {CYAN}[8]{RESET} Generate Auth-Aware BOLA Reports")
    print()


# ============================================================
# 1. BOLA / IDOR LOCAL LAB
# ============================================================

def bola_lab():
    heading("BOLA / IDOR SCANNER — LOCAL LAB")

    # These ports belong to the project's documented lab fixtures.
    # Never terminate processes that were not started by this function.
    ports = [8000, 8001]

    for port in ports:
        if port_is_open("127.0.0.1", port):
            print_status(
                "STOP",
                f"Port {port} sedang digunakan.",
                YELLOW,
            )
            print(
                "Matikan server lab yang kamu jalankan sendiri, "
                "atau pastikan port tersebut memang untuk lab API Sentinel."
            )
            return

    test_script = SRC / "bola_test.py"
    secure_script = SRC / "mock_api.py"
    vulnerable_script = SRC / "mock_api_vulnerable_lab.py"

    required = [test_script, secure_script, vulnerable_script]
    missing = [str(p) for p in required if not p.is_file()]

    if missing:
        print_status("ERROR", "File lab berikut tidak ditemukan:", RED)
        for item in missing:
            print(f"    - {item}")
        return

    report = REPORTS / "bola_comparison.json"
    if report.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = BACKUPS / f"bola_comparison_before_cli_{timestamp}.json"

        try:
            shutil.copy2(report, backup)
            print_status("BACKUP", str(backup.relative_to(ROOT)), GREEN)
        except OSError as exc:
            print_status(
                "ERROR",
                f"Gagal membuat backup laporan: {exc}",
                RED,
            )
            print("Pengujian dibatalkan untuk menjaga laporan lama.")
            return

    processes = []

    try:
        print_status("INFO", "Menjalankan fixture API lokal...", CYAN)

        secure_log = open(REPORTS / "secure_lab.log", "w")
        secure_process = subprocess.Popen(
            [PYTHON, str(secure_script)],
            cwd=ROOT,
            stdout=secure_log,
            stderr=subprocess.STDOUT,
        )
        processes.append((secure_process, secure_log))

        vulnerable_log = open(REPORTS / "vulnerable_lab.log", "w")
        vulnerable_process = subprocess.Popen(
            [PYTHON, str(vulnerable_script)],
            cwd=ROOT,
            stdout=vulnerable_log,
            stderr=subprocess.STDOUT,
        )
        processes.append((vulnerable_process, vulnerable_log))

        # Wait for the two local fixtures to start.
        for _ in range(30):
            secure_ready = port_is_open("127.0.0.1", 8000)
            vulnerable_ready = port_is_open("127.0.0.1", 8001)

            if secure_ready and vulnerable_ready:
                break

            if secure_process.poll() is not None:
                raise RuntimeError(
                    "Secure fixture berhenti saat startup. "
                    "Periksa reports/secure_lab.log."
                )

            if vulnerable_process.poll() is not None:
                raise RuntimeError(
                    "Vulnerable fixture berhenti saat startup. "
                    "Periksa reports/vulnerable_lab.log."
                )

            time.sleep(0.5)

        if not port_is_open("127.0.0.1", 8000):
            raise RuntimeError(
                "Secure fixture tidak aktif pada port 8000."
            )

        if not port_is_open("127.0.0.1", 8001):
            raise RuntimeError(
                "Vulnerable fixture tidak aktif pada port 8001."
            )

        print_status("OK", "Kedua fixture lokal siap.", GREEN)

        if not run_script("bola_test.py"):
            print_status(
                "WARN",
                "Scanner gagal. Laporan baru mungkin tidak lengkap.",
                YELLOW,
            )
            return

        if run_script("regression_test.py"):
            print_status(
                "OK",
                "Regression test berhasil. Membuat laporan...",
                GREEN,
            )
            generate_reports(quiet=True)
        else:
            print_status(
                "WARN",
                "Regression test gagal. Periksa laporan sebelum "
                "menggunakannya sebagai bukti.",
                YELLOW,
            )

    except KeyboardInterrupt:
        print_status("STOP", "Pengujian dihentikan.", YELLOW)
    except (OSError, RuntimeError) as exc:
        print_status("ERROR", str(exc), RED)
    finally:
        for process, log_file in reversed(processes):
            if process.poll() is None:
                process.terminate()

            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

            log_file.close()

        print_status("INFO", "Fixture yang dibuat oleh CLI sudah dihentikan.", CYAN)


# ============================================================
# 2. OPENAPI AUDIT
# ============================================================

def spec_audit():
    heading("OPENAPI SPECIFICATION AUDIT")

    spec_path = ROOT / "examples" / "openapi.yaml"

    if not spec_path.is_file():
        print_status(
            "ERROR",
            f"Spec tidak ditemukan: {spec_path.relative_to(ROOT)}",
            RED,
        )
        return

    print_status("INFO", "Memeriksa dokumentasi OpenAPI contoh.", CYAN)
    print_status(
        "NOTE",
        "Hasil audit spesifikasi bukan bukti bahwa endpoint runtime rentan.",
        YELLOW,
    )

    run_script("spec_audit.py")


# ============================================================
# 3. HTTP CHECKS — LOCALHOST ONLY
# ============================================================

def http_check():
    heading("HTTP SECURITY CHECKS")

    print("  Pemeriksaan ini dibatasi ke API di komputer sendiri.")
    print("  Contoh URL: http://127.0.0.1:8000")
    print("  HTTPS, domain publik, dan alamat jaringan lain tidak diterima.")
    print()

    url = input("  Masukkan base URL localhost: ").strip()

    # Explicit allowlist. Do not accept arbitrary hosts.
    allowed_prefixes = (
        "http://127.0.0.1",
        "http://localhost",
    )

    if not url.startswith(allowed_prefixes):
        print_status(
            "DENIED",
            "Hanya URL HTTP localhost yang diizinkan.",
            RED,
        )
        return

    # Parse and validate host/port rather than relying only on prefix.
    from urllib.parse import urlsplit

    try:
        parsed = urlsplit(url)
        hostname = (parsed.hostname or "").lower()

        if (
            parsed.scheme != "http"
            or hostname not in {"127.0.0.1", "localhost"}
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            print_status("DENIED", "Format URL tidak diizinkan.", RED)
            return

        if parsed.port is not None and not (1 <= parsed.port <= 65535):
            print_status("DENIED", "Port tidak valid.", RED)
            return

        if not parsed.path:
            url = url.rstrip("/")

    except ValueError:
        print_status("ERROR", "URL tidak valid.", RED)
        return

    env = os.environ.copy()
    env["API_SENTINEL_BASE_URL"] = url

    print_status("INFO", f"Target lab: {url}", CYAN)
    run_script("http_checker.py", env=env)


# ============================================================
# 4. VIEW REPORTS
# ============================================================

def view_reports():
    heading("REPORT CENTER")

    files = sorted(
        p for p in REPORTS.iterdir()
        if p.is_file()
    )

    if not files:
        print_status("INFO", "Belum ada laporan.", YELLOW)
        return

    print("  Laporan yang tersedia:\n")

    for index, path in enumerate(files, start=1):
        size = path.stat().st_size
        print(
            f"  {CYAN}[{index}]{RESET} "
            f"{path.name} {DIM}({size} bytes){RESET}"
        )

    print(f"\n  {CYAN}[0]{RESET} Kembali")
    choice = input("\n  Pilih laporan: ").strip()

    if choice == "0":
        return

    try:
        index = int(choice)
        if index < 1 or index > len(files):
            raise ValueError
        selected = files[index - 1]
    except ValueError:
        print_status("ERROR", "Pilihan tidak valid.", RED)
        return

    if selected.suffix.lower() == ".html":
        print_status(
            "INFO",
            f"Laporan HTML: {selected.relative_to(ROOT)}",
            CYAN,
        )
        print("  Buka secara manual dengan browser:")
        print(f"  file://{selected.resolve()}")
        return

    heading(f"REPORT: {selected.name}")

    try:
        content = selected.read_text(
            encoding="utf-8",
            errors="replace",
        )

        max_chars = 16000
        if len(content) > max_chars:
            content = content[:max_chars]
            content += "\n\n[Output dipotong agar terminal tetap ringan.]"

        print(content)

    except OSError as exc:
        print_status("ERROR", str(exc), RED)


# ============================================================
# 5. GENERATE REPORTS
# ============================================================

def generate_reports(quiet=False):
    if not quiet:
        heading("REPORT GENERATOR")

    markdown_ok = run_script("markdown_report.py")
    html_ok = run_script("html_report.py")

    if markdown_ok and html_ok:
        print_status(
            "DONE",
            "Pembuatan laporan Markdown dan HTML selesai.",
            GREEN,
        )
        print(f"  Lokasi: {REPORTS.relative_to(ROOT)}/")
    elif not quiet:
        print_status(
            "WARN",
            "Sebagian laporan mungkin belum dibuat. "
            "Periksa pesan error di atas.",
            YELLOW,
        )


# ============================================================
# ============================================================
# AUTH-AWARE BOLA TESTS
# ============================================================

def auth_bola_tests():
    heading("AUTH-AWARE BOLA TESTS")

    if not (SRC / "auth_bola_test.py").is_file():
        status("ERROR", "src/auth_bola_test.py tidak ditemukan.", RED)
        return

    print("  Target: localhost lab")
    print("  Pengujian: autentikasi dan otorisasi objek")
    print("  Pastikan mock API berjalan pada port 8000.")
    print()

    confirm = input("  Jalankan 6 skenario pengujian? (y/N): ").strip().lower()
    if confirm != "y":
        status("INFO", "Pengujian dibatalkan.", YELLOW)
        return

    env = os.environ.copy()
    env.setdefault("API_SENTINEL_BASE_URL", "http://127.0.0.1:8000")
    run_script("auth_bola_test.py", env=env)


def auth_bola_report():
    heading("GENERATE AUTH-AWARE BOLA REPORTS")

    report_json = SRC.parent / "reports" / "auth_bola_report.json"

    if not (SRC / "auth_report.py").is_file():
        print_status(
            "ERROR",
            "src/auth_report.py tidak ditemukan.",
            RED,
        )
        return

    if not report_json.is_file():
        print_status(
            "ERROR",
            "Laporan JSON belum ada. Jalankan menu 7 terlebih dahulu.",
            RED,
        )
        return

    print("  Output:")
    print("    reports/auth_bola_report.md")
    print("    reports/auth_bola_report.html")
    print()
    confirm = input("  Buat ulang laporan dari JSON yang ada? (y/N): ").strip().lower()

    if confirm != "y":
        print_status("INFO", "Pembuatan laporan dibatalkan.", YELLOW)
        return

    if run_script("auth_report.py"):
        print_status("OK", "Laporan Auth-Aware BOLA berhasil dibuat.", GREEN)
    else:
        print_status("ERROR", "Generator laporan gagal. Periksa pesan di atas.", RED)


# MAIN LOOP
# ============================================================

def main():
    while True:
        show_banner()
        show_menu()

        try:
            choice = input(f"{BOLD}api-sentinel > {RESET}").strip()

            if choice == "1":
                bola_lab()
                pause()

            elif choice == "2":
                spec_audit()
                pause()

            elif choice == "3":
                http_check()
                pause()

            elif choice == "4":
                view_reports()
                pause()

            elif choice == "5":
                generate_reports()
                pause()

            elif choice == "6":
                print()
                print_status("EXIT", "API Sentinel ditutup. Stay secure!", GREEN)
                break

            elif choice == "7":
                auth_bola_tests()
                pause()

            elif choice == "8":
                auth_bola_report()
                pause()

            else:
                print_status(
                    "ERROR",
                    "Pilihan tidak dikenal. Pilih angka 1 sampai 8.",
                    RED,
                )
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n")
            print_status("INFO", "Kembali ke menu...", YELLOW)
            time.sleep(0.5)


if __name__ == "__main__":
    main()
