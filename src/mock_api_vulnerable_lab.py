
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


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path

        if not path.startswith("/orders/"):
            self.send_json(404, {"error": "Not found"})
            return

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

        # FIXTURE LAB: sengaja tidak memeriksa pemilik pesanan.
        self.send_json(200, {
            "order_id": order_id,
            "item": order["item"],
        })

    def log_message(self, fmt, *args):
        print(f"[LOCAL LAB] {args[0]}")


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8001), Handler)
    print("Vulnerable BOLA fixture: http://127.0.0.1:8001")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLab stopped.")
    finally:
        server.server_close()
