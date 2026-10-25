# API Sentinel — Auth-Aware BOLA Assessment

**Version:** 1.1.0
**Generated:** 2026-10-25T13:11:06.943343+00:00
**Scope:** localhost lab only
**Target:** `http://127.0.0.1:8000`

## Summary

- Total tests: 6
- Passed: 6
- Failed: 0
- Errors: 0

## Test results

| Test | Path | Expected | Actual | Result |
|---|---|---:|---:|---|
| Alice reads own order | `/orders/1001` | 200 | 200 | PASS |
| Alice reads Bob's order | `/orders/1002` | 403 | 403 | PASS |
| Bob reads own order | `/orders/1002` | 200 | 200 | PASS |
| Unauthenticated request | `/orders/1001` | 401 | 401 | PASS |
| Invalid token | `/orders/1001` | 401 | 401 | PASS |
| Nonexistent order | `/orders/999999` | 404 | 404 | PASS |

## Evidence

### Alice reads own order

- Method: `GET`
- Path: `/orders/1001`
- Expected status: `200`
- Actual status: `200`
- Result: **PASS**

Response evidence:

```json
{
  "order_id": "1001",
  "item": "Laptop"
}
```

### Alice reads Bob's order

- Method: `GET`
- Path: `/orders/1002`
- Expected status: `403`
- Actual status: `403`
- Result: **PASS**

Response evidence:

```json
{
  "error": "Forbidden"
}
```

### Bob reads own order

- Method: `GET`
- Path: `/orders/1002`
- Expected status: `200`
- Actual status: `200`
- Result: **PASS**

Response evidence:

```json
{
  "order_id": "1002",
  "item": "Keyboard"
}
```

### Unauthenticated request

- Method: `GET`
- Path: `/orders/1001`
- Expected status: `401`
- Actual status: `401`
- Result: **PASS**

Response evidence:

```json
{
  "error": "Unauthorized"
}
```

### Invalid token

- Method: `GET`
- Path: `/orders/1001`
- Expected status: `401`
- Actual status: `401`
- Result: **PASS**

Response evidence:

```json
{
  "error": "Unauthorized"
}
```

### Nonexistent order

- Method: `GET`
- Path: `/orders/999999`
- Expected status: `404`
- Actual status: `404`
- Result: **PASS**

Response evidence:

```json
{
  "error": "Not found"
}
```

## Limitations

- Only predefined local lab cases were tested.
- Passing these tests does not prove overall API security.
- This report does not assign a CVSS score.

This report describes only the configured local lab tests. Passing the tests is not proof of overall API security.
