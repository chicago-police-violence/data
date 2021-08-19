from utils import csv_read, flatten_stars
from collections import defaultdict
from matcher import Matcher
from datasets import datasets
from csv import DictWriter


def f1(officer, m):
    s = set(u["uid"] for u in m[officer])
    if len(s) == 1:
        return s.pop()


f1.key = ["first_name", "last_name", "race", "gender", "appointment_date", "birthyear"]


def f2(officer, m):
    s = set(
        u["uid"]
        for u in m[officer]
        if officer["star"] != "" and officer["star"] in set(u["stars"])
    )
    if len(s) == 1:
        return s.pop()


f3 = lambda o, m: f1(o, m)
f3.key = ["last_name", "gender", "birthyear", "appointment_date"]
# f3.debug = True

f4 = lambda o, m: f1(o, m)
f4.key = ["first_name", "gender", "birthyear", "appointment_date"]


if __name__ == "__main__":

    from sys import argv
    import os.path

    root, _ = os.path.splitext(os.path.basename(argv[2]))
    id_fields = datasets[root]["id_fields"]

    d = defaultdict(list)
    for row in csv_read(argv[2]):
        key = tuple(row[f] for f in id_fields)
        d[key].append(row)

    officers = []
    for key in d:
        officer = dict(zip(id_fields, key))
        officer["last_name"], officer["first_name"] = officer["name"].rsplit(", ", 1)
        officers.append(officer)

    m = Matcher(flatten_stars(profile) for profile in csv_read(argv[3]))
    linked, unlinked = m.match(officers, [f1, f2, f3, f4])

    profiles = list(m.unify(linked, unlinked, matchee_source=root))
    fields = datasets["P0-58155"]["fields"]
    fields += [f for f in datasets["P4-41436"]["fields"] if f not in fields]
    fields += ["source", "uid"]

    with open(argv[3], "w") as pf:
        pw = DictWriter(pf, fieldnames=fields, extrasaction="ignore")
        pw.writeheader()
        for profile in profiles:
            pw.writerow(profile)

    with open(argv[1], "w") as pf:
        fields = [f for f in datasets[root]["fields"] if f not in id_fields]
        fields += ["uid"]
        w = DictWriter(pf, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for profile in profiles:
            if profile["source"] == root:
                key = tuple(profile[f] for f in id_fields)
                for row in d[key]:
                    row["uid"] = profile["uid"]
                    rowdict = {k: row[k] for k in fields}
                    w.writerow(rowdict)
