import copy
import json
from typing import Dict, List, Optional, Set, Union
from uuid import uuid4

_DATA_FILE_NAME = "data/test.json"


class DatabaseStoredTree:
    """
    This class emulates an interface (driver) to some database that
    stores the tree structure.
    I have decided to store it like key-value pairs.
    Each record has its data and list of children's ids.

    I miss error handling in the whole project because lack of time.
    But I remember of that
    """

    def __init__(self, initial_data: Dict) -> None:
        self._initial_data = initial_data
        self._db = copy.deepcopy(initial_data)

    def get_leaf(self, position: str) -> Dict[str, Dict]:
        return {position: self._db[position]}

    def update_db(self, data: Dict[str, Dict]) -> None:
        for key, item in data.items():
            self._db[key] = item

    def get_new_id(self) -> str:
        while True:
            rundom_id = str(uuid4())
            if rundom_id not in self._db:
                return rundom_id

    def reset(self) -> None:
        self._db = copy.deepcopy(self._initial_data)


class CacheStoredTree:
    """
    This class implements a cache where users can do their business with a tree node.
    """

    def __init__(self, database: DatabaseStoredTree):
        """Constructor
        Args:
            database (DatabaseStoredTree): Instance of the hypothetical database driver
        """
        self._cache: Dict = {}
        self._database = database

    def get_leaf(self, key: str) -> Union[Dict, None]:
        item: Optional[Dict] = self._cache.get(key, None)
        if item and not item.get("deleted", False):
            return {key: item}
        else:
            return None

    def get_all_roots(self) -> List[Dict]:
        """[summary]
        Sometimes we need information about nodes that don't have their parents in the cache
        Returns:
            List[Dict]: List of that nodes
        """
        storage = self._cache
        return self.get_all_roots_for_storage(storage)

    def load_leaf_to_cache(self, key: str) -> None:
        self._cache.update(self._database.get_leaf(key))

    def insert_leaf(self, parent: str, data: str) -> str:
        if not self._cache[parent].get("deleted", False):
            item_id = self._database.get_new_id()
            self._cache[item_id] = {"data": data, "children": []}
            self._cache[parent]["children"].append(item_id)
        else:
            raise KeyError(parent)
        return item_id

    def change_leaf_data(self, leaf_key: str, data: str) -> None:
        if not self._cache[leaf_key].get("deleted", False):
            self._cache[leaf_key]["data"] = data

    def delete(self, leaf_key: str) -> None:
        """[summary]
            In order to delete all children, I used the list type in a stack-like manner
        Args:
            leaf_key (str)
        """
        delete_stack: List = []

        self._cache[leaf_key]["deleted"] = True
        cached_items_ids: Set = set(self._cache.keys())
        delete_stack.extend(cached_items_ids.intersection(self._cache[leaf_key]["children"]))

        while delete_stack:
            child = delete_stack.pop()
            self._cache[child]["deleted"] = True
            delete_stack.extend(cached_items_ids.intersection(self._cache[child]["children"]))

    def get_copy_except_deleted(self) -> Dict[str, Dict]:
        """[summary]
            To convert data to format that jstree library use to show tree
            I make a copy of the cache structure.
        Returns:
            Dict[str, Dict]
        """
        cache_copy = {
            key: value for key, value in copy.deepcopy(self._cache).items() if not value.get("deleted", False)
        }
        return cache_copy

    def flush_data_to_db(self) -> None:
        self._database.update_db(self._cache)

    def reset(self) -> None:
        self._cache.clear()
        self._database.reset()

    @staticmethod
    def get_all_roots_for_storage(storage: Dict) -> List[Dict]:
        cached_items_ids: Set = set(storage.keys())
        keys_set: Set = set(storage.keys())

        for item in storage.values():
            children = cached_items_ids.intersection(item["children"])
            keys_set.difference_update(children)

        result: List[Dict] = [{key: storage[key]} for key in keys_set if not storage[key].get("deleted", False)]
        return result


with open(_DATA_FILE_NAME) as file:
    db = DatabaseStoredTree(json.load(file))
    cache = CacheStoredTree(db)
