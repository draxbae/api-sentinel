
import json
from pathlib import Path

import yaml


def load_openapi(file_path: str) -> dict:
    """Load an OpenAPI document from JSON or YAML."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Specification not found: {path}")

    content = path.read_text(encoding="utf-8")

    if path.suffix.lower() == ".json":
        document = json.loads(content)
    else:
        document = yaml.safe_load(content)

    if not isinstance(document, dict):
        raise ValueError("OpenAPI document must be an object")

    if not str(document.get("openapi", "")).startswith("3."):
        raise ValueError("An OpenAPI 3.x specification is required")

    return document


def map_endpoints(document: dict) -> list[dict]:
    """Extract paths and HTTP methods from an OpenAPI document."""
    endpoints = []
    methods = {
        "get", "post", "put", "patch", "delete",
        "options", "head", "trace"
    }

    for path, path_item in document.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue

        for method, details in path_item.items():
            if method.lower() not in methods:
                continue

            details = details if isinstance(details, dict) else {}

            endpoints.append({
                "path": path,
                "method": method.upper(),
                "operation_id": details.get("operationId"),
                "summary": details.get("summary"),
                "security_defined": (
                    "security" in details
                    or "security" in document
                ),
            })

    return endpoints
