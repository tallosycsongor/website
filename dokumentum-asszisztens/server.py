from __future__ import annotations

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from core import Journal, safe_root, scan

BASE = Path(__file__).resolve().parent
STATE = BASE / ".local"
CONFIG = STATE / "config.json"
JOURNAL = Journal(STATE / "operations.sqlite3")


def load_config() -> dict:
    if not CONFIG.exists():
        return {"root": ""}
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def save_config(data: dict) -> dict:
    root = safe_root(str(data.get("root", "")))
    STATE.mkdir(parents=True, exist_ok=True)
    value = {"root": str(root)}
    CONFIG.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    return value


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE / "public"), **kwargs)

    def json_response(self, status: int, value):
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length) or b"{}")

    def root(self):
        value = load_config().get("root")
        if not value:
            raise ValueError("Előbb állítsd be a kezelendő mappát.")
        return safe_root(value)

    def do_GET(self):
        route = urlparse(self.path).path
        try:
            if route == "/api/status":
                return self.json_response(200, {"config": load_config(), "offline": True})
            if route == "/api/scan":
                return self.json_response(200, {"files": scan(self.root())})
            if route == "/api/history":
                return self.json_response(200, {"operations": JOURNAL.list()})
            return super().do_GET()
        except Exception as error:
            self.json_response(400, {"error": str(error)})

    def do_POST(self):
        route = urlparse(self.path).path
        try:
            data = self.body()
            if route == "/api/config":
                return self.json_response(200, {"config": save_config(data)})
            if route == "/api/apply":
                return self.json_response(200, {"operation": JOURNAL.move(self.root(), data.get("source", ""), data.get("target", ""))})
            if route == "/api/undo":
                return self.json_response(200, {"operation": JOURNAL.undo(self.root(), int(data.get("id", 0)))})
            self.json_response(404, {"error": "Ismeretlen végpont."})
        except Exception as error:
            self.json_response(400, {"error": str(error)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3011"))
    print(f"Dokumentum Asszisztens: http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
