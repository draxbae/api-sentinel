from openapi_parser import load_openapi, map_endpoints


def main():
    spec = load_openapi("examples/openapi.yaml")
    endpoints = map_endpoints(spec)

    print("=== API SENTINEL v0.1 ===")
    print(f"Endpoints discovered: {len(endpoints)}")

    for endpoint in endpoints:
        print(
            f"[{endpoint['method']}] {endpoint['path']}"
            f" | {endpoint['summary']}"
        )


if __name__ == "__main__":
    main()
