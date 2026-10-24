# API Sentinel — Security Assessment

**Versi:** 1.0.0
**Dibuat:** 2026-10-24T20:41:48.364140+00:00
**Cakupan:** Lab BOLA/IDOR lokal

## Ringkasan

- Target lab diuji: 2
- Total pengujian: 12
- Temuan potensial: 1

| Target lab | Pengujian | PASS | FINDING |
|---|---:|---:|---:|
| secure | 6 | 6 | 0 |
| vulnerable_lab | 6 | 5 | 1 |

## Temuan

### 1. Potensi BOLA / IDOR

- **Target lab:** `http://127.0.0.1:8001`
- **Pengujian:** Alice reads Bob's order
- **ID objek:** `1002`
- **Status HTTP yang diharapkan:** `403`
- **Status HTTP aktual:** `200`
- **Bukti:** Cross-owner data was exposed.

**Rekomendasi:** Terapkan pemeriksaan otorisasi di sisi server untuk setiap objek dan pastikan pengguna yang terautentikasi memiliki izin mengakses objek yang diminta.

## Batasan

Pengujian ini hanya menggunakan fixture lokal yang sengaja dibuat untuk demonstrasi. Temuan bukan bukti kerentanan pada sistem produksi. Validasi tambahan diperlukan sebelum menentukan tingkat risiko nyata.

**Sumber:** `reports/bola_comparison.json`
