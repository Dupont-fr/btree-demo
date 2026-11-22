"""WSGI entry point for deployment on WSGI hosts (Render, PythonAnywhere, gunicorn)."""
import json
import os
import mimetypes
import threading

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

from tree_ops import build_tree, BST, RBTree, BST_EXAMPLE, RB_EXAMPLE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


def _read_body(environ):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    if length <= 0:
        return b""
    return environ["wsgi.input"].read(length)


def _json_response(start_response, obj, status="200 OK"):
    data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(data))),
        ("Access-Control-Allow-Origin", "*"),
    ]
    start_response(status, headers)
    return [data]


def _serve_file(start_response, path):
    if not os.path.isfile(path):
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"Not found"]
    ctype, _ = mimetypes.guess_type(path)
    if ctype is None:
        ctype = "application/octet-stream"
    with open(path, "rb") as f:
        data = f.read()
    start_response("200 OK", [("Content-Type", ctype), ("Content-Length", str(len(data)))])
    return [data]


def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")

    if method == "OPTIONS":
        start_response("204 No Content", [
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type"),
        ])
        return [b""]

    if path == "/" or path == "":
        return _serve_file(start_response, os.path.join(STATIC_DIR, "index.html"))

    if path.startswith("/static/"):
        rel = path[len("/static/"):]
        full = os.path.join(STATIC_DIR, rel)
        if not os.path.abspath(full).startswith(os.path.abspath(STATIC_DIR)):
            start_response("403 Forbidden", [("Content-Type", "text/plain")])
            return [b"Forbidden"]
        return _serve_file(start_response, full)

    if path == "/api/apply" and method == "POST":
        raw = _read_body(environ)
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            return _json_response(start_response, {"ok": False, "error": "JSON invalide"}, "400 Bad Request")
        tree_type = payload.get("type", "bst")
        if tree_type not in ("bst", "rb"):
            return _json_response(start_response, {"ok": False, "error": "type invalide"}, "400 Bad Request")
        op = payload.get("op", "")
        snap = payload.get("tree", None)
        value = payload.get("value", None)
        try:
            from tree_ops import build_tree
            t = build_tree(tree_type, snap)
        except Exception as e:
            return _json_response(start_response, {"ok": False, "error": f"arbre invalide: {e}"}, "400 Bad Request")
        try:
            if op == "reset":
                nt = BST() if tree_type == "bst" else RBTree()
                return _json_response(start_response, {"ok": True, "tree": nt.snapshot(), "steps": [],
                    "stats": nt.stats(), "result": None, "violations": None})
            if op == "example":
                nt = BST() if tree_type == "bst" else RBTree()
                seq = BST_EXAMPLE if tree_type == "bst" else RB_EXAMPLE
                for v in seq:
                    nt.insert(v)
                return _json_response(start_response, {"ok": True, "tree": nt.snapshot(), "steps": [],
                    "stats": nt.stats(), "result": None, "violations": None, "message": "Arbre exemple charge."})
            if op == "insert":
                steps = t.insert(int(value))
            elif op == "delete":
                steps = t.delete(int(value))
            elif op == "search":
                steps = t.search(int(value))
            elif op == "min":
                steps = t.minimum()
            elif op == "max":
                steps = t.maximum()
            elif op == "succ":
                steps = t.successor(int(value))
            elif op == "pred":
                steps = t.predecessor(int(value))
            elif op == "rotate_left":
                steps = t.rotate_left(int(value))
            elif op == "rotate_right":
                steps = t.rotate_right(int(value))
            elif op in ("preorder", "inorder", "postorder", "bfs"):
                res = {"preorder": t.preorder, "inorder": t.inorder, "postorder": t.postorder, "bfs": t.breadth_first}[op]()
                return _json_response(start_response, {"ok": True, "tree": t.snapshot(), "steps": [],
                    "stats": t.stats(), "result": res, "violations": None})
            elif op == "validate":
                v = t.validate()
                return _json_response(start_response, {"ok": True, "tree": t.snapshot(), "steps": [],
                    "stats": t.stats(), "result": None, "violations": v})
            elif op == "traversals_all":
                return _json_response(start_response, {"ok": True, "tree": t.snapshot(), "steps": [],
                    "stats": t.stats(), "result": {"largeur": t.breadth_first(), "prefixe": t.preorder(),
                        "infixe": t.inorder(), "postfixe": t.postorder()}, "violations": None})
            else:
                raise ValueError(f"operation inconnue: {op}")
            return _json_response(start_response, {"ok": True, "tree": t.snapshot(), "steps": steps,
                "stats": t.stats(), "result": None, "violations": None})
        except Exception as e:
            return _json_response(start_response, {"ok": False, "error": str(e)}, "400 Bad Request")

    if path == "/api/reviews":
        if method == "GET":
            return _json_response(start_response, {"ok": True, "reviews": _load_reviews()})
        if method == "POST":
            raw = _read_body(environ)
            try:
                payload = json.loads(raw.decode("utf-8")) if raw else {}
            except Exception:
                return _json_response(start_response, {"ok": False, "error": "JSON invalide"}, "400 Bad Request")
            name = (payload.get("name") or "").strip()[:60]
            message = (payload.get("message") or "").strip()[:500]
            if not name or not message:
                return _json_response(start_response, {"ok": False, "error": "Nom et message requis"}, "400 Bad Request")
            import datetime
            review = {
                "name": name,
                "message": message,
                "date": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            }
            reviews = _load_reviews()
            reviews.insert(0, review)
            reviews = reviews[:100]
            _save_reviews(reviews)
            return _json_response(start_response, {"ok": True, "review": review, "reviews": reviews})

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not found"]
