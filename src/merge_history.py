from utils import csv_read
from matcher import Matcher
from collections import defaultdict
from uuid import uuid4
from itertools import chain
from datetime import date


def comp_age(officer1, officer2):
    if officer2["age"] == "" and officer1["birthyear"] == "":
        return True
    birthyear = 2016 - int(officer2["age"])
    return int(officer1["birthyear"]) in [birthyear, birthyear - 1]


def flatten_history(changes, officer_attributes):
    hist_key = ["unit_number", "start_date", "end_date"]
    officers = defaultdict(list)
    for change in changes:
        officer_key = tuple(change[k] for k in officer_attributes)
        officers[officer_key].append(tuple(change[k] for k in hist_key))
    for o, history in officers.items():
        officer = dict(zip(officer_attributes, o))
        officer["history"] = sorted(history, key=lambda e: e[1])
        yield officer


def f1(officer, m):
    if officer["appointment_date"] >= "2016-02-29":
        officer["uid"] = uuid4()
        return
    for o in (officers := m[officer]) :
        if comp_age(officer, o) and before(o, officer):
            return o
    else:
        if officer["history"] == sorted(
            (e for o in officers for e in o["history"]), key=lambda e: e[1]
        ):
            return [({**officer, "history": o["history"]}, o) for o in officers]


f1.key = ["last_name", "first_name", "gender", "appointment_date"]


def f2(officer, m):
    for o in (officers := m[officer]) :
        if comp_age(officer, o) and before(o, officer):
            return o


f2.key = ["first_name", "gender", "race", "appointment_date"]


def f3(officer, m):
    return f2(officer, m)


f3.key = ["last_name", "gender", "race", "appointment_date"]


def before(old, new):
    h1, h2 = old["history"], new["history"]
    if (n := len(h1)) > len(h2):
        return False
    else:
        return all(
            h2[i] == h1[i]
            or (i == (n - 1) and h2[i][:2] == h1[i][:2] and h1[i][2] == "")
            for i in range(n)
        )


if __name__ == "__main__":
    key = ["last_name", "first_name", "gender", "race", "appointment_date", "age"] + [
        f"star{i}" for i in range(1, 11)
    ]
    officers = flatten_history(csv_read("parsed/16-1105.csv"), key)
    m = Matcher(officers)

    key = [
        "last_name",
        "first_name",
        "gender",
        "race",
        "appointment_date",
        "middle_initial",
        "birthyear",
    ]
    officers = flatten_history(csv_read("parsed/P0-52262.csv"), key)
    linked, unlinked = m.match(officers, [f1, f2, f3])
    for o in unlinked:
        print(o)
    r1 = {o["uid"]: o for o in chain(m, m._removed)}
    r2 = {o["uid"]: o for o in linked if o["uid"] in r1}
