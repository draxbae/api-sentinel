# API Sentinel — Security Assessment

**Versi:** 0.8.0
**Dibuat:** 2026-10-24T17:43:36.440341+00:00
**Cakupan:** Lab BOLA/IDOR lokal

## Ringkasan

- Target lab diuji: 2
- Total pengujian: 8
- Temuan potensial: 1

| Target lab | Pengujian | PASS | FINDING |
|---|---:|---:|---:|
| secure | 4 | 4 | 0 |
| vulnerable_lab | 4 | 3 | 1 |

## Temuan

### 1. Potensi BOLA / IDOR

- **Target lab:** `http://127.0.0.1:8001`
- **Pengujian:** Alice reads Bob's order
- **ID objek:** `1002`
- **Status HTTP yang diharapkan:** `403`
- **Status HTTP aktual:** `200`
- **Bukti:** Alice received Bob's order data: potential BOLA in local lab.

**Rekomendasi:** Terapkan pemeriksaan otorisasi di sisi server untuk setiap objek dan pastikan pengguna yang terautentikasi memiliki izin mengakses objek yang diminta.

## Batasan

Pengujian ini hanya menggunakan fixture lokal yang sengaja dibuat untuk demonstrasi. Temuan bukan bukti kerentanan pada sistem produksi. Validasi tambahan diperlukan sebelum menentukan tingkat risiko nyata.

**Sumber:** `reports/bola_comparison_v0.8.0.json`
