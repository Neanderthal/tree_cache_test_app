from typing import Dict, List

from flask import abort, request
from flask_smorest import Blueprint

from .core import CacheStoredTree, cache, db

api_bp = Blueprint("api", __name__, url_prefix="/")


def get_leaf_for_jstree(child: Dict, child_id: str) -> Dict:
    _, body = child.popitem()
    return {
        "id": child_id,
        "text": body.get("data", ""),
        "children": bool(body.get("children", False)),
        "state": {"disabled": True} if body.get("deleted", False) else {},
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
        _, body = db.get_leaf(item_id).popitem()
        for child_id in body.get("children", []):
            child = db.get_leaf(child_id)
            result.append(get_leaf_for_jstree(child, child_id))
        return result


@api_bp.route("cache_tree_full/", methods=["GET"])
@api_bp.response(200)
def cache_tree_full() -> List[Dict]:
    """
        This API method returns the cached tree
        Here I convert the tree stored in a hash table to the common view tree
        which jstree library uses to display the tree.
        I use the list in a stack-like manner to do that.
    Returns:
        List[Dict]
    """
    cache_copy = cache.get_cache_copy()

    items_stack = []
    items_stack.extend(CacheStoredTree.get_all_roots_for_storage(cache_copy))

    if not items_stack:
        return []

    while items_stack:
        item_key, value = items_stack.pop().popitem()
        if "children" in value:
            children_ids = value["children"].copy()
            value["children"].clear()

            for child_id in children_ids:
                if child_id in cache_copy:
                    items_stack.append({child_id: cache_copy.get(child_id)})
                    value["children"].append(cache_copy[child_id])
                    del cache_copy[child_id]

        value["id"] = item_key
        value["text"] = value["data"]
        if value.get("deleted", False):
            value["state"] = {"disabled": True}
        del value["data"]

    return list(cache_copy.values())


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
    cache.flush_data_to_db()
    return "flushed"


@api_bp.route("reset/", methods=["POST"])
@api_bp.response(200)
def reset() -> str:
    cache.reset()
    return "reseted"
