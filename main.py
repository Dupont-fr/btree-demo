import os
import json
import mimetypes
import threading
import datetime

REVIEWS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviews.json")
_reviews_lock = threading.Lock()

def _load_reviews():
    with _reviews_lock:
        if not os.path.isfile(REVIEWS_FILE):
            return []
        try:
            with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:
            return []
        return []

def _save_reviews(reviews):
    with _reviews_lock:
        with open(REVIEWS_FILE, "w", encoding="utf-8") as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote

from tree_ops import (
    build_tree, BST, RBTree, BST_EXAMPLE, RB_EXAMPLE,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


def _json_response(handler, obj, status=200):
    data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(data)


def _serve_file(handler, path):
    if not os.path.isfile(path):
        handler.send_error(404, "Not found")
        return
    ctype, _ = mimetypes.guess_type(path)
    if ctype is None:
        ctype = "application/octet-stream"
    with open(path, "rb") as f:
        data = f.read()
    handler.send_response(200)
    handler.send_header("Content-Type", ctype)
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path == "/" or path == "":
            _serve_file(self, os.path.join(STATIC_DIR, "index.html"))
            return
        if path.startswith("/static/"):
            rel = path[len("/static/"):]
            full = os.path.join(STATIC_DIR, rel)
            # prevent traversal
            if not os.path.abspath(full).startswith(os.path.abspath(STATIC_DIR)):
                self.send_error(403)
                return
            _serve_file(self, full)
            return
        if path == "/api/reviews":
            _json_response(self, {"ok": True, "reviews": _load_reviews()})
            return
        self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/reviews":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b""
            try:
                payload = json.loads(raw.decode("utf-8")) if raw else {}
            except Exception:
                _json_response(self, {"ok": False, "error": "JSON invalide"}, 400)
                return
            name = (payload.get("name") or "").strip()[:60]
            message = (payload.get("message") or "").strip()[:500]
            if not name or not message:
                _json_response(self, {"ok": False, "error": "Nom et message requis"}, 400)
                return
            review = {"name": name, "message": message, "date": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")}
            reviews = _load_reviews()
            reviews.insert(0, review)
            reviews = reviews[:100]
            _save_reviews(reviews)
            _json_response(self, {"ok": True, "review": review, "reviews": reviews})
            return
        if parsed.path != "/api/apply":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            _json_response(self, {"ok": False, "error": "JSON invalide"}, 400)
            return

        tree_type = payload.get("type", "bst")
        if tree_type not in ("bst", "rb"):
            _json_response(self, {"ok": False, "error": "type invalide"}, 400)
            return
        op = payload.get("op", "")
        snap = payload.get("tree", None)
        value = payload.get("value", None)

        try:
            t = build_tree(tree_type, snap)
        except Exception as e:
            _json_response(self, {"ok": False, "error": f"arbre invalide: {e}"}, 400)
            return

        try:
            if op == "reset":
                nt = BST() if tree_type == "bst" else RBTree()
                _json_response(self, {
                    "ok": True, "tree": nt.snapshot(), "steps": [],
                    "stats": nt.stats(), "result": None, "violations": None,
                })
                return

            if op == "example":
                nt = BST() if tree_type == "bst" else RBTree()
                seq = BST_EXAMPLE if tree_type == "bst" else RB_EXAMPLE
                for v in seq:
                    nt.insert(v)
                _json_response(self, {
                    "ok": True, "tree": nt.snapshot(), "steps": [],
                    "stats": nt.stats(), "result": None, "violations": None,
                    "message": "Arbre exemple chargé.",
                })
                return

            if op == "insert":
                if value is None:
                    raise ValueError("value requise")
                steps = t.insert(int(value))
            elif op == "delete":
                if value is None:
                    raise ValueError("value requise")
                steps = t.delete(int(value))
            elif op == "search":
                if value is None:
                    raise ValueError("value requise")
                steps = t.search(int(value))
            elif op == "min":
                steps = t.minimum()
            elif op == "max":
                steps = t.maximum()
            elif op == "succ":
                if value is None:
                    raise ValueError("value requise")
                steps = t.successor(int(value))
            elif op == "pred":
                if value is None:
                    raise ValueError("value requise")
                steps = t.predecessor(int(value))
            elif op == "rotate_left":
                if value is None:
                    raise ValueError("value requise")
                steps = t.rotate_left(int(value))
            elif op == "rotate_right":
                if value is None:
                    raise ValueError("value requise")
                steps = t.rotate_right(int(value))
            elif op in ("preorder", "inorder", "postorder", "bfs"):
                if op == "preorder":
                    res = t.preorder()
                elif op == "inorder":
                    res = t.inorder()
                elif op == "postorder":
                    res = t.postorder()
                else:
                    res = t.breadth_first()
                _json_response(self, {
                    "ok": True, "tree": t.snapshot(), "steps": [],
                    "stats": t.stats(), "result": res, "violations": None,
                })
                return
            elif op == "validate":
                v = t.validate()
                _json_response(self, {
                    "ok": True, "tree": t.snapshot(), "steps": [],
                    "stats": t.stats(), "result": None, "violations": v,
                })
                return
            elif op == "traversals_all":
                _json_response(self, {
                    "ok": True, "tree": t.snapshot(), "steps": [],
                    "stats": t.stats(), "result": {
                        "largeur": t.breadth_first(),
                        "prefixe": t.preorder(),
                        "infixe": t.inorder(),
                        "postfixe": t.postorder(),
                    },
                    "violations": None,
                })
                return
            else:
                raise ValueError(f"operation inconnue: {op}")

            _json_response(self, {
                "ok": True, "tree": t.snapshot(), "steps": steps,
                "stats": t.stats(), "result": None, "violations": None,
            })
        except Exception as e:
            _json_response(self, {"ok": False, "error": str(e)}, 400)

    def log_message(self, *args):
        pass


def main():
    port = int(os.environ.get("PORT", "8000"))
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving on http://0.0.0.0:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
