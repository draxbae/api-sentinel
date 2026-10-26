
import argparse

from openapi_parser import load_openapi, map_endpoints


def audit_spec(document: dict) -> list[dict]:
    findings = []

    for endpoint in map_endpoints(document):
        path = endpoint["path"]
        method = endpoint["method"]

        operation = next(
            (
                details
                for candidate_path, path_item in document.get("paths", {}).items()
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

        if "security" not in operation and "security" not in document:
            findings.append({
                "severity": "REVIEW",
                "endpoint": f"{method} {path}",
                "issue": "No explicit security requirement",
            })

    return findings


def main():
    parser = argparse.ArgumentParser(
        description="Audit an OpenAPI 3.x specification."
    )
    parser.add_argument(
        "spec_path",
        nargs="?",
        default="examples/openapi.yaml",
        help="Path to an OpenAPI JSON/YAML file",
    )
    args = parser.parse_args()

    try:
        spec = load_openapi(args.spec_path)
        findings = audit_spec(spec)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print("=== API SENTINEL SPEC AUDIT ===")
    print(f"Specification: {args.spec_path}")
    print(f"Potential documentation issues: {len(findings)}")

    for finding in findings:
        print(
            f"[{finding['severity']}] "
            f"{finding['endpoint']} - {finding['issue']}"
        )


if __name__ == "__main__":
    main()
