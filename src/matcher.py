from collections import defaultdict
from itertools import chain
from uuid import uuid4
import logging


class Matcher:
    def __init__(self, items=[], key_attributes=["uid"]):
        self._index = defaultdict(list)
        self._dict = defaultdict(list)
        self._key_attr = key_attributes
        self._matched = []
        for item in items:
            self.add(item)

    def __getitem__(self, item):
        return self._index[self.key(item)]

    def __contains__(self, item):
        return self.key(item) in self._index

    def add(self, item):
        if "uid" not in item:
            item["uid"] = uuid4()
        self._dict[item["uid"]].append(item)

    def key(self, elem):
        return tuple(elem[k] for k in self._key_attr)

    def __delitem__(self, uid):
        for elem in self._dict[uid]:
            elems = self[elem]
            elems.remove(elem)
            if len(elems) == 0:
                del self._index[self.key(elem)]
        del self._dict[uid]

    def index(self, key_attributes):
        self._key_attr = key_attributes
        self._index = defaultdict(list)
        for item_list in self._dict.values():
            for item in item_list:
                self._index[self.key(item)].append(item)

    def __iter__(self):
        return iter(self._dict.values())

    def __len__(self):
        return len(self._dict)

    def matched(self):
        return iter(self._matched)

    def matching_pass(self, f, linked, unlinked, remove):
        if hasattr(f, "key"):
            self.index(f.key)
        next_unlinked = list()
        for item in unlinked:
            match = f(item, self)
            if type(match) is list:
                for (new, matched) in match:
                    new["uid"] = matched
                    linked.append(new)
                    if remove:
                        self._matched.append(self._dict[matched])
                        del self[matched]
                continue
            if match is not None:
                if type(item) is list:
                    for u in item:
                        u["uid"] = match
                elif type(item) is dict:
                    item["uid"] = match
                else:
                    continue
                if getattr(f, "debug", False):
                    logging.debug((self._dict[match], item))
                if remove:
                    self._matched.append(self._dict[match])
                    del self[match]
            if (type(item) is list and all("uid" in u for u in item)) or (
                type(item) is dict and "uid" in item
            ):
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

    def unify(self, linked, unlinked, matcher_source=None, matchee_source=None):
        for elems in chain(self, self.matched()):
            for elem in elems:
                if matcher_source is not None:
                    elem["source"] = matcher_source
                yield elem
        for elem in linked:
            if type(elem) is dict:
                elem = [elem]
            for e in elem:
                if matchee_source is not None:
                    e["source"] = matchee_source
                yield e
        for elem in unlinked:
            if type(elem) is dict:
                elem = [elem]
            for e in elem:
                if matchee_source is not None:
                    e["source"] = matchee_source
                e["uid"] = uuid4()
                yield e
