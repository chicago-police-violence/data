from collections import defaultdict
from uuid import uuid4
import logging


class Matcher:
    def __init__(self, items=[], key_attributes=["uid"]):
        self._index = defaultdict(list)
        self._key_attr = key_attributes
        self._removed = []
        for item in items:
            self.add(item)

    def __getitem__(self, item):
        return self._index[self.key(item)]

    def __contains__(self, item):
        return self.key(item) in self._index

    def add(self, item):
        if "uid" not in item:
            item["uid"] = uuid4()
        self._index[self.key(item)].append(item)

    def key(self, elem):
        return tuple(elem[k] for k in self._key_attr)

    def __delitem__(self, officer):
        key = self.key(officer)
        officers = self._index[key]
        officers.remove(officer)
        self._removed.append(officer)
        if len(officers) == 0:
            del self._index[key]

    def index(self, key_attributes):
        old = self._index
        self._key_attr = key_attributes
        self._index = defaultdict(list)
        for item_list in old.values():
            for item in item_list:
                self.add(item)

    def __iter__(self):
        return (item for item_list in self._index.values() for item in item_list)

    def __len__(self):
        return sum(len(item_list) for item_list in self._index.values())

    def removed(self):
        return iter(self._removed)

    def matching_pass(self, f, linked, unlinked, remove):
        if hasattr(f, "key"):
            self.index(f.key)
        next_unlinked = list()
        for item in unlinked:
            matching_item = f(item, self)
            if type(matching_item) is list:
                for (new, matched) in matching_item:
                    new["uid"] = matched["uid"]
                    linked.append(new)
                    if remove:
                        del self[matched]
                continue
            if matching_item is not None:
                item["uid"] = matching_item["uid"]
                if getattr(f, "debug", False):
                    logging.debug(item)
                    logging.debug(matching_item)
                if remove:
                    del self[matching_item]
            if "uid" in item:
                linked.append(item)
            else:
                next_unlinked.append(item)
        return linked, next_unlinked

    def match(self, items, funs, remove=True):
        linked, unlinked = [], list(items)
        logging.info(f"Matching {len(unlinked)} items")
        for f in funs:
            total = len(linked) + len(unlinked)
            linked, unlinked = self.matching_pass(f, linked, unlinked, remove)
            assert len(linked) + len(unlinked) >= total
            logging.info(f"Matched: {len(linked)}, Unmatched: {len(unlinked)}")
        return linked, unlinked