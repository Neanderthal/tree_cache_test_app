from flask import request, abort
from flask_smorest import Blueprint
from typing import List, Dict
from .core import cache, db

api_bp = Blueprint("api", __name__, url_prefix="/")


def get_leaf_for_jstree(child: Dict, child_id: str) -> Dict:
    return {
        "id": child_id,
        "text": child[child_id]["data"],
        "children": bool(child[child_id]["children"]),
    }


@api_bp.route("main_tree/", methods=["GET"])
@api_bp.response(200)
def main_tree() -> List:
    item_id = request.args.get("id")

    if not item_id or item_id == "#":
        child = db.get_leaf("root")
        data = [
            get_leaf_for_jstree(child, "root"),
        ]
        return data
    else:
        result = []
        leaf = db.get_leaf(item_id)
        for child_id in leaf[item_id]["children"]:
            child = db.get_leaf("root")
            result.append(get_leaf_for_jstree(child, child_id))
        return result


@api_bp.route("cache_tree/", methods=["GET"])
@api_bp.response(200)
def cache_tree() -> List[Dict]:
    item_id = request.args.get("id")
    print(f"FUCK {id}")

    if not item_id or item_id == "#":
        result = []
        roots = cache.get_all_roots()
        for root in roots:
            root_id, value str = root.popitem
            result.append(get_leaf_for_jstree(root, root_id))
        print(result)
        return result
    else:
        result = []
        leaf = cache.get_leaf(item_id)
        if leaf:
            for child_id in leaf[item_id]["children"]:
                child = cache.get_leaf(child_id)
                if child:
                    result.append(
                        {
                            "id": child_id,
                            "text": child[child_id]["data"],
                            "children": bool(child[child_id]["children"]),
                        }
                    )
        return result


@api_bp.route("move_node/", methods=["PUT"])
@api_bp.response(200)
def move_node() -> str:
    item_id = request.form.get("id", None)
    if item_id:
        cache.load_leaf_to_cache(item_id)
        return f"{item_id} moved"
    else:
        abort(400)


@api_bp.route("delete_node/", methods=["DELETE"])
@api_bp.response(200)
def delete_node() -> str:
    item_id = request.form.get("id", None)
    if item_id:
        cache.delete(item_id)
        return f"{item_id} deleted"
    else:
        abort(400)


@api_bp.route("add_node/", methods=["PUT"])
@api_bp.response(200)
def add_node() -> str:
    input_data = request.form.get("input_data", None)
    parent_node_id = request.form.get("parent_node_id", None)
    if input_data and parent_node_id:
        item_id = cache.insert_leaf(parent_node_id, input_data)
        return f"{item_id} added"
    else:
        abort(400)


@api_bp.route("update_node/", methods=["POST"])
@api_bp.response(200)
def update_node() -> str:
    input_data = request.form.get("input_data", None)
    node_id = request.form.get("id", None)
    if input_data and node_id:
        cache.change_leaf_data(node_id, input_data)
        return f"{node_id} updated"
    else:
        abort(400)


@api_bp.route("flush/", methods=["POST"])
@api_bp.response(200)
def flush() -> str:
    cache.pour_to_db()
    return "flushed"


@api_bp.route("reset/", methods=["POST"])
@api_bp.response(200)
def reset() -> str:
    cache.reset()
    return "reseted"
