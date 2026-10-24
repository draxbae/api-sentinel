
from openapi_parser import load_openapi, map_endpoints


def audit_spec(document: dict) -> list[dict]:
    findings = []

    for endpoint in map_endpoints(document):
        path = endpoint["path"]
        method = endpoint["method"]

        operation = next(
            (
                details
                for candidate_path, path_item
                in document.get("paths", {}).items()
                if candidate_path == path
                for candidate_method, details in path_item.items()
                if candidate_method.upper() == method
            ),
            {},
        )

        if not operation.get("responses"):
            findings.append({
                "severity": "INFO",
                "endpoint": f"{method} {path}",
                "issue": "No documented responses",
            })

        if (
            "security" not in operation
            and "security" not in document
        ):
            findings.append({
                "severity": "REVIEW",
                "endpoint": f"{method} {path}",
                "issue": "No explicit security requirement",
            })

    return findings


if __name__ == "__main__":
    spec = load_openapi("examples/openapi.yaml")
    findings = audit_spec(spec)

    print("=== API SENTINEL SPEC AUDIT ===")
    print(f"Potential documentation issues: {len(findings)}")

    for finding in findings:
        print(
            f"[{finding['severity']}] "
            f"{finding['endpoint']} - {finding['issue']}"
        )
