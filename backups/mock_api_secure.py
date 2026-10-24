from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse

ORDERS = {
    "1001": {"owner": "alice", "item": "Laptop"},
    "1002": {"owner": "bob", "item": "Keyboard"},
}

TOKENS = {
    "alice-token": "alice",
    "bob-token": "bob",
}


class MockAPIHandler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/profile":
            self.send_json(200, {"id": 1, "name": "Lab User"})
            return

        if path == "/admin/users":
            self.send_json(403, {"error": "Forbidden"})
            return

        if path.startswith("/orders/"):
            order_id = path.rsplit("/", 1)[-1]
            order = ORDERS.get(order_id)

            if order is None:
                self.send_json(404, {"error": "Not found"})
                return

            token = self.headers.get("Authorization", "")
            username = TOKENS.get(token.removeprefix("Bearer "))

            if username is None:
                self.send_json(401, {"error": "Unauthorized"})
                return

            # Implementasi aman: hanya pemilik pesanan yang dapat membacanya.
            if order["owner"] != username:
                self.send_json(403, {"error": "Forbidden"})
                return

            self.send_json(200, {
                "order_id": order_id,
                "item": order["item"],
            })
            return

        self.send_json(404, {"error": "Not found"})

    def log_message(self, format, *args):
        print(f"[LAB] {args[0]}")


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), MockAPIHandler)
    print("API Sentinel BOLA lab running at http://127.0.0.1:8000")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMock API stopped.")
    finally:
        server.server_close()
