"""Smoke tests for Khaana competitive API."""
import json, threading, urllib.request
from src.app import H
from http.server import ThreadingHTTPServer

def _start():
    httpd = ThreadingHTTPServer(("127.0.0.1", 18765), H)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd

def get(path):
    with urllib.request.urlopen(f"http://127.0.0.1:18765{path}") as r:
        return json.loads(r.read())

def post(path, body):
    req = urllib.request.Request(f"http://127.0.0.1:18765{path}", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def test_flow():
    httpd = _start()
    try:
        assert get("/health")["ok"]
        assert get("/capabilities")["competitor"] == "Foodpanda"
        v = get("/vendors?city=Karachi")
        assert v["count"] >= 1
        post("/cart/add", {"user": "u1", "vendor_id": "v1", "item_id": "m1", "qty": 2})
        o = post("/checkout", {"user": "u1", "coupon": "WELCOME100", "payment_method": "cod", "address": "DHA"})
        assert o["ok"] and o["order"]["total_pkr"] > 0
        tid = o["order"]["id"]
        post(f"/orders/{tid}/advance", {})
        tr = get(f"/orders/{tid}/track")
        assert tr["status"] in ("confirmed", "preparing", "out_for_delivery", "delivered")
        print("khaana tests OK")
    finally:
        httpd.shutdown()

if __name__ == "__main__":
    test_flow()
