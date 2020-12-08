from utils import csv_read
from matcher import Matcher
from collections import defaultdict
from uuid import uuid4
from itertools import chain
from datetime import date
from csv import DictWriter


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


def comp_age(officer1, officer2):
    if officer2["age"] == "" and officer1["birthyear"] == "":
        return True
    birthyear = 2016 - int(officer2["age"])
    return int(officer1["birthyear"]) in [birthyear, birthyear - 1]


def flatten_history(changes, id_attributes):
    hist_key = ["unit_no", "start_date", "end_date"]
    officers = defaultdict(list)
    for change in changes:
        key = tuple(change[k] for k in id_attributes)
        officers[key].append(tuple(change[k] for k in hist_key))
    for key, history in officers.items():
        officer = dict(zip(id_attributes, key))
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
f3 = lambda o, m: f2(o, m)
f3.key = ["last_name", "gender", "race", "appointment_date"]


if __name__ == "__main__":
    key = ["last_name", "first_name", "gender", "race", "appointment_date", "age"] + [
        f"star{i}" for i in range(1, 11)
    ]
    officers = flatten_history(csv_read("parsed/16-1105.csv"), key)
    m = Matcher(officers)

    nkey = [
        "last_name",
        "first_name",
        "gender",
        "race",
        "appointment_date",
        "middle_initial",
        "birthyear",
    ]
    officers = flatten_history(csv_read("parsed/P0-52262.csv"), nkey)
    linked, unlinked = m.match(officers, [f1, f2, f3])

    officers = defaultdict(list)
    history = dict()
    for o in chain(m, m.removed(), linked):
        officers[o["uid"]].append(o)
        del o["uid"]
    for o in unlinked:
        o["uid"] = uuid4()
        officers[o["uid"]].append(o)
        del o["uid"]

    from link_history import link

    m, linked, unlinked = link(officers.values())
    fieldnames = [
        "last_name",
        "first_name",
        "middle_initial",
        "gender",
        "race",
        "birthyear",
        "age",
        "status",
        "appointment_date",
        "position_no",
        "position_description",
        "unit_no",
        "unit_description",
        "resignation_date",
    ]
    fieldnames += ["star" + str(i) for i in range(1, 12)]
    fieldnames += ["star", "sworn", "unid_id", "unit_detail", "uid", "source"]

    with open("linked/profiles.csv", "w") as pf, open("linked/history.csv", "w") as hf:
        pw = DictWriter(pf, fieldnames=fieldnames, extrasaction="ignore")
        hw = DictWriter(
            hf, fieldnames=["uid", "start_date", "end_date"], extrasaction="ignore"
        )
        pw.writeheader()
        hw.writeheader()
        for l in unlinked:
            uid = uuid4()
            for u in l:
                u["uid"] = uid
        for o in chain(linked, unlinked, m._dict.values(), m.removed()):
            for u in o:
                pw.writerow(u)
