import json
import math
from pathlib import Path
from threading import Lock

from flask import Flask, jsonify, request, url_for
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "users.json"
ITEMS_FILE = BASE_DIR / "items.json"
catalog_lock = Lock()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_items(items):
    temporary_file = ITEMS_FILE.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(items, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_file.replace(ITEMS_FILE)


@app.before_request
def require_basic_auth():
    if request.endpoint not in {"items_collection", "item_detail"}:
        return None

    auth = request.authorization
    if auth and auth.type == "basic" and auth.username and auth.password:
        password_hash = read_json(USERS_FILE).get(auth.username)
        if password_hash and check_password_hash(password_hash, auth.password):
            return None

    return (
        jsonify(error="Valid Basic Auth credentials are required"),
        401,
        {"WWW-Authenticate": 'Basic realm="Store Catalog"'},
    )


@app.errorhandler(HTTPException)
def handle_http_error(error):
    response = error.get_response()
    response.set_data(app.json.dumps({"error": error.description}))
    response.content_type = "application/json"
    return response


def parse_item():
    if not request.is_json:
        return None, (jsonify(error="Use Content-Type: application/json"), 415)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify(error="Expected a JSON object"), 400)

    name = data.get("name")
    price = data.get("price")
    color = data.get("color")

    if not isinstance(name, str) or not name.strip():
        return None, (jsonify(error="name must be a non-empty string"), 400)
    if type(price) not in (int, float) or price < 0 or (
        isinstance(price, float) and not math.isfinite(price)
    ):
        return None, (jsonify(error="price must be a non-negative number"), 400)
    if not isinstance(color, str) or not color.strip():
        return None, (jsonify(error="color must be a non-empty string"), 400)

    return {"name": name.strip(), "price": price, "color": color.strip()}, None


@app.route("/items", methods=["GET", "POST"])
def items_collection():
    with catalog_lock:
        items = read_json(ITEMS_FILE)
        if request.method in {"GET", "HEAD"}:
            return jsonify(items)

        fields, error = parse_item()
        if error is not None:
            return error

        item_id = max((item["id"] for item in items), default=0) + 1
        item = {"id": item_id, **fields}
        items.append(item)
        save_items(items)
        return jsonify(item), 201, {"Location": url_for("item_detail", item_id=item_id)}


@app.route("/items/<int:item_id>", methods=["GET", "PUT", "DELETE"])
def item_detail(item_id):
    with catalog_lock:
        items = read_json(ITEMS_FILE)
        index = next((i for i, item in enumerate(items) if item["id"] == item_id), None)
        if index is None:
            return jsonify(error="Item not found"), 404

        if request.method in {"GET", "HEAD"}:
            return jsonify(items[index])

        if request.method == "DELETE":
            items.pop(index)
            save_items(items)
            return jsonify(message="Item deleted", id=item_id)

        fields, error = parse_item()
        if error is not None:
            return error

        item = {"id": item_id, **fields}
        items[index] = item
        save_items(items)
        return jsonify(item)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001)
