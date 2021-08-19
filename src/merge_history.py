from utils import csv_read
from matcher import Matcher
from collections import defaultdict
from uuid import uuid4
from itertools import chain
from datetime import date
from csv import DictWriter
from datasets import datasets


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
        return uuid4()
    for o in (officers := m[officer]) :
        if comp_age(officer, o) and before(o, officer):
            return o["uid"]
    else:
        if officer["history"] == sorted(
            (e for o in officers for e in o["history"]), key=lambda e: e[1]
        ):
            return [({**officer, "history": o["history"]}, o["uid"]) for o in officers]


f1.key = ["last_name", "first_name", "gender", "appointment_date"]


def f2(officer, m):
    for o in (officers := m[officer]) :
        if comp_age(officer, o) and before(o, officer):
            return o["uid"]


f2.key = ["first_name", "gender", "race", "appointment_date"]
f3 = lambda o, m: f2(o, m)
f3.key = ["last_name", "gender", "race", "appointment_date"]


if __name__ == "__main__":
    from sys import argv
    import os.path

    s1, _ = os.path.splitext(os.path.basename(argv[2]))
    s2, _ = os.path.splitext(os.path.basename(argv[3]))

    officers = flatten_history(csv_read(argv[2]), datasets[s1]["id_fields"])
    m = Matcher(officers)

    officers = flatten_history(csv_read(argv[3]), datasets[s2]["id_fields"])
    linked, unlinked = m.match(officers, [f1, f2, f3])

    officers = defaultdict(list)
    for o in m.unify(linked, unlinked, s1, s2):
        officers[o["uid"]].append(o)
        del o["uid"]

    from link_history import link

    m, linked, unlinked = link(officers.values(), argv[4])
    fields = datasets["P0-58155"]["fields"]
    fields += [f for f in datasets["P4-41436"]["fields"] if f not in fields]
    fields += ["source", "uid"]

    profiles = list(m.unify(linked, unlinked))

    with open(argv[4], "w") as pf:
        pw = DictWriter(pf, fieldnames=fields, extrasaction="ignore")
        pw.writeheader()
        for profile in profiles:
            pw.writerow(profile)

    history = defaultdict(list)
    for profile in profiles:
        if "history" in profile:
            history[profile["uid"]].append(profile)

    with open(argv[1], "w") as hf:
        fields = ["uid", "unit_no", "start_date", "end_date"]
        hw = DictWriter(hf, fieldnames=fields, extrasaction="ignore")
        hw.writeheader()
        for profiles in history.values():
            p = None
            if len(profiles) == 1:
                p = profiles[0]
            elif len(profiles) == 2:
                for pr in profiles:
                    if pr["source"] == "P0-52262":
                        p = pr
                        break
            for e in p["history"]:
                hw.writerow(dict(zip(fields, [p["uid"]] + list(e))))
