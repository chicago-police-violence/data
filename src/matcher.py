from collections import defaultdict
from itertools import chain
from uuid import UUID, uuid4
import logging


class Matcher:
    """
    A class to represent a collection of records to which new records can be matched.
    """

    def __init__(self, records=[], key_attributes=["uid"]):
        self._dict = defaultdict(list)
        """Collection of records. Maps a uid to list of records with this uid."""

        self._index = defaultdict(list)
        """Collection index. Maps an index key to a list of records with this key."""

        self._key_attr = key_attributes
        """List of record attributes used to index the records."""

        # initialize the collection
        for record in records:
            self.add(record)
        self.index()

    def add(self, record):
        """Adds a record to the collection, used at initialization."""
        if "uid" not in record:
            record["uid"] = uuid4()
        self._dict[record["uid"]].append(record)

    def key(self, record):
        """Computes the index key of a record."""
        return tuple(record[k] for k in self._key_attr)

    def index(self, key_attributes=None):
        """Rebuilds the collection index."""
        if key_attributes is not None:
            self._key_attr = key_attributes
        self._index = defaultdict(list)
        for record_list in self:
            for record in record_list:
                self._index[self.key(record)].append(record)

    def __getitem__(self, record):
        """Returns the list of records with the same key as `record`.

        Called when using `self[record]`."""
        return self._index[self.key(record)]

    def __contains__(self, record):
        """Called when using `record in self`."""
        return self.key(record) in self._index

    def __iter__(self):
        """Implements the sequence model."""
        return iter(self._dict.values())

    def __len__(self):
        return len(self._dict)

    def __delitem__(self, uid):
        """Removes a uid from the collection."""
        for record in self._dict[uid]:
            # first we remove each record with the given uid from the index
            records = self[record]
            records.remove(record)
            if len(records) == 0: # no record left with same index key as `elem`
                del self._index[self.key(record)]
        del self._dict[uid] #finally we remove the uid

    def matched(self):
        return iter(self._matched)

    def matching_pass(self, f, linked, unlinked, remove):
        """Performs a single pass of the iterative pairwise matching procedure.

        Args:
            f: Matching criterion.
            linked: List to which records are added as they are matched.
            unlinked: List of records to match against the collection.
            remove: Boolean, remove records from collection when they are matched against.
        """

        if hasattr(f, "key"):
            self.index(f.key)
        next_unlinked = list()
        for item in unlinked:
            match = f(item, self)
            if isinstance(match, list):
                for (new, matched) in match:
                    new["uid"] = matched
                    linked.append(new)
                    if remove:
                        self._matched.append(self._dict[matched])
                        del self[matched]
            elif isinstance(match, UUID) or isinstance(match, str):
                if type(item) is list: # item to be matched is a list of records
                    for u in item:
                        u["uid"] = match
                elif type(item) is dict: # item to be matched is a single record
                    item["uid"] = match
                else:
                    raise TypeError("Item to be matched is neither a list or a disct.")

                if getattr(f, "debug", False):
                    logging.debug((self._dict[match], item))
                linked.append(item)
                if remove:
                    self._matched.append(self._dict[match])
                    del self[match]
            else:
                # matching criterion `f` returned `None`
                # item is added to list of unlinked records
                # possibly to be matched in the next pass
                next_unlinked.append(item)
        return linked, next_unlinked

    def match(self, records, funs, remove=True):
        """Matches records to the collection using iterative pairwise matching.

        Args:
            records: The list of records to match.
            funs: The list of functions ot use as a macthing citerion at each pass.
        """

        self._matched = []
        linked, unlinked = [], list(records)
        logging.info(f"Matching {len(unlinked)} records")
        for f in funs:
            total = len(linked) + len(unlinked)
            linked, unlinked = self.matching_pass(f, linked, unlinked, remove)
            assert len(linked) + len(unlinked) >= total
            logging.info(f"Matched: {len(linked)}, Unmatched: {len(unlinked)}")
        return linked, unlinked

    def unify(self, linked, unlinked, matcher_source=None, matchee_source=None):
        """Iterates over list of all records (matched and unmatched ones).

        Used at the end of the pairwise iterative matching to collect all records."""
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
            uid = uuid4()
            for e in elem:
                if matchee_source is not None:
                    e["source"] = matchee_source
                e["uid"] = uid
                yield e
