#%%
import copy
from typing import Dict, List, Set, Union, Optional
from uuid import uuid4

_DATA_STRUCT: Dict = {
    "root": {"data": "Res", "children": ["2", "3"]},
    "2": {"data": "Child 1", "children": ["4"]},
    "3": {"data": "Child 2", "children": ["5"]},
    "4": {"data": "Child 4", "children": ["6"]},
    "5": {"data": "Child 5", "children": []},
    "6": {"data": "Child 6", "children": ["7", "8"]},
    "7": {"data": "Child 7", "children": []},
    "8": {"data": "Child 8", "children": []},
}


class DatabaseStoredTree:
    def __init__(self, initial_data: Dict) -> None:
        self._initial_data = initial_data
        self._db = copy.deepcopy(initial_data)

    def get_leaf(self, position: str) -> Dict[str, Dict]:
        return {position: _DATA_STRUCT[position]}

    def update_db(self, data: Dict[str, Dict]) -> None:
        for key, item in data.items():
            _DATA_STRUCT[key] = item

    def get_new_id(self) -> str:
        while True:
            rundom_id = str(uuid4())
            if rundom_id not in _DATA_STRUCT:
                return rundom_id

    def reset(self) -> None:
        self._db = copy.deepcopy(self._initial_data)


class CacheStoredTree:
    def __init__(self, database: DatabaseStoredTree):
        self._cache: Dict = {}
        self._database = database

    def get_leaf(self, position: str) -> Union[Dict, None]:
        item: Optional[Dict] = self._cache.get(position, None)
        if item and not item.get("deleted", False):
            return {position: item}
        else:
            return None

    def get_all_roots(self) -> List[Dict]:
        storage = self._cache
        return self.get_all_roots_for_storage(storage)

    def load_leaf_to_cache(self, position: str) -> None:
        self._cache.update(self._database.get_leaf(position))

    def insert_leaf(self, parent: str, data: str) -> str:
        if not self._cache[parent].get("deleted", False):
            item_id = self._database.get_new_id()
            self._cache[item_id] = {"data": data, "children": []}
            self._cache[parent]["children"].append(item_id)
        else:
            raise KeyError(parent)
        return item_id

    def change_leaf_data(self, item: str, data: str) -> None:
        if not self._cache[item].get("deleted", False):
            self._cache[item]["data"] = data
        else:
            raise KeyError(item)

    def delete(self, item: str) -> None:
        delete_stack: List = []

        self._cache[item]["deleted"] = True
        cached_items_ids: Set = set(self._cache.keys())
        delete_stack.extend(cached_items_ids.intersection(self._cache[item]["children"]))

        while delete_stack:
            child = delete_stack.pop()
            self._cache[child]["deleted"] = True
            delete_stack.extend(cached_items_ids.intersection(self._cache[child]["children"]))

    def get_tree_traversal(self):
        # [{
        #    "id":1,"text":"Root node","children":[
        #        {"id":2,"text":"Child node 1"},
        #        {"id":3,"text":"Child node 2"}
        #    ]
        # }]

        cache_copy = copy.deepcopy(self._cache)

        items_stack = []
        items_stack.extend(CacheStoredTree.get_all_roots_for_storage(cache_copy))

        while items_stack:
            item_key, value = items_stack.pop().popitem()
            if "children" in value:
                children_ids = value["children"].copy()
                value["children"].clear()
                for child_id in children_ids:
                    items_stack.append({child_id: cache_copy[child_id]})
                    value["children"].append(cache_copy[child_id])
                    del cache_copy[child_id]
            value["id"] = item_key
            value["text"] = value["data"]
            del value["data"]

        return cache_copy

    def pour_to_db(self) -> None:
        self._database.update_db(self._cache)

    def reset(self) -> None:
        self._cache.clear()
        self._database.reset()

    @staticmethod
    def get_all_roots_for_storage(storage):
        cached_items_ids: Set = set(storage.keys())
        keys_set: Set = set(storage.keys())

        for item in storage.values():
            children = cached_items_ids.intersection(item["children"])
            keys_set.difference_update(children)

        result: List[Dict] = [{key: storage[key]} for key in keys_set if not storage[key].get("deleted", False)]
        return result


db = DatabaseStoredTree(_DATA_STRUCT)
cache = CacheStoredTree(db)

cache._cache = _DATA_STRUCT
cache.get_tree_traversal()
# %%
