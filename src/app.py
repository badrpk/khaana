"""Khaana — multi-vendor food marketplace API (demo)."""
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

VENDORS = [
    {"id": "v1", "name": "Karachi Biryani House", "city": "Karachi", "rating": 4.7},
    {"id": "v2", "name": "Lahore Grill", "city": "Lahore", "rating": 4.5},
    {"id": "v3", "name": "Islamabad Healthy Bowls", "city": "Islamabad", "rating": 4.6},
]
MENU = {
    "v1": [{"id": "m1", "name": "Chicken Biryani", "price_pkr": 450}, {"id": "m2", "name": "Raita", "price_pkr": 80}],
    "v2": [{"id": "m3", "name": "Seekh Kebab", "price_pkr": 600}, {"id": "m4", "name": "Naan", "price_pkr": 50}],
    "v3": [{"id": "m5", "name": "Quinoa Bowl", "price_pkr": 750}],
}
CARTS: dict[str, list] = {}

class H(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        data = json.dumps(obj, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802
        p = urlparse(self.path)
        if p.path in ("/", "/health"):
            return self._json(200, {"ok": True, "service": "khaana", "product": "Multi-vendor food marketplace API"})
        if p.path == "/vendors":
            return self._json(200, {"ok": True, "vendors": VENDORS})
        if p.path.startswith("/vendors/") and p.path.endswith("/menu"):
            vid = p.path.split("/")[2]
            return self._json(200, {"ok": True, "vendor_id": vid, "menu": MENU.get(vid, [])})
        if p.path == "/cart":
            q = parse_qs(p.query)
            uid = (q.get("user") or ["guest"])[0]
            return self._json(200, {"ok": True, "user": uid, "items": CARTS.get(uid, [])})
        self._json(404, {"ok": False, "error": "not found", "routes": ["/", "/vendors", "/vendors/{id}/menu", "/cart?user="]})

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            return self._json(400, {"ok": False, "error": "invalid json"})
        if self.path == "/cart/add":
            uid = str(body.get("user") or "guest")
            item = {"vendor_id": body.get("vendor_id"), "item_id": body.get("item_id"), "qty": int(body.get("qty") or 1)}
            CARTS.setdefault(uid, []).append(item)
            return self._json(200, {"ok": True, "cart": CARTS[uid]})
        if self.path == "/order":
            uid = str(body.get("user") or "guest")
            items = CARTS.get(uid, [])
            if not items:
                return self._json(400, {"ok": False, "error": "cart empty"})
            order = {"id": f"ord_{len(CARTS)}", "user": uid, "items": items, "status": "placed"}
            CARTS[uid] = []
            return self._json(200, {"ok": True, "order": order})
        self._json(404, {"ok": False, "error": "not found"})

    def log_message(self, *a):
        return

def main():
    print("Khaana food API http://127.0.0.1:8765  (GET /vendors)")
    HTTPServer(("127.0.0.1", 8765), H).serve_forever()

if __name__ == "__main__":
    main()
