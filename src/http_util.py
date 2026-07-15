
"""Minimal stdlib JSON HTTP helpers — no third-party deps required."""
from __future__ import annotations
import json, time, uuid, hashlib, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from typing import Any

def uid(prefix: str = "id") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"

def now() -> float:
    return time.time()

def iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

class JsonAPI(BaseHTTPRequestHandler):
    server_version = "ParityService/1.0"
    def log_message(self, fmt, *args):  # quieter
        return
    def _read_json(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        raw = self.rfile.read(n)
        try:
            return json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            return {"_error": "invalid_json"}
    def _send(self, code: int, obj: Any):
        data = json.dumps(obj, indent=2, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_OPTIONS(self):
        self._send(204, {})
    def parse(self):
        p = urlparse(self.path)
        return p.path.rstrip("/") or "/", parse_qs(p.query)

def serve(handler_cls, host="127.0.0.1", port=8765, name="service"):
    httpd = ThreadingHTTPServer((host, port), handler_cls)
    print(f"{name} listening on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nshutdown")
