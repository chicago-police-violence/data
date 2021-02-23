from datasets import datasets
from collections import defaultdict
from utils import csv_read, flatten_stars
from matcher import Matcher
from csv import DictWriter

def f1(officer, m):
    s = set(u["uid"] for u in m[officer])
    if len(s) == 1:
        return s.pop()


f1.key = ["first_name", "last_name", "race", "gender", "appointment_date"]

def f2(officer, m):
    s = set(
        u["uid"]
        for u in m[officer]
        if officer["star"] != "" and officer["star"] in set(u["stars"])
    )
    if len(s) == 1:
        return s.pop()

if __name__ == "__main__":
    import os.path
    from sys import argv

    root, _ = os.path.splitext(os.path.basename(argv[1]))
    id_fields = datasets[root]["id_fields"] + ["star"]

    stars = {row["trr_id"]: row["star"] for row in csv_read(argv[2])}
    d = defaultdict(list)
    for row in csv_read(argv[1]):
        if row["number_of_weapons_discharged"] not in ["", 0]:
            row["star"] = stars[row["trr_id"]]
            key = tuple(row[f] for f in id_fields)
            d[key].append(row)
    officers = [dict(zip(id_fields, key), rows=rows) for key, rows in d.items()]

    m = Matcher(flatten_stars(profile) for profile in csv_read(argv[3]))
    linked, unlinked = m.match(officers, [f1, f2])

    profiles = list(m.unify(linked, unlinked, matchee_source=root))
    fields = datasets["P0-58155"]["fields"]
    fields += [f for f in datasets["P4-41436"]["fields"] if f not in fields]
    fields += ["source", "uid"]

    with open(argv[3], "w") as pf:
        pw = DictWriter(pf, fieldnames=fields, extrasaction="ignore")
        pw.writeheader()
        for profile in profiles:
            pw.writerow(profile)

    with open(argv[4], "w") as pf:
        fields = [f for f in datasets[root]["fields"] if f not in id_fields]
        fields += ["uid"]
        w = DictWriter(pf, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for officer in officers:
            for row in officer["rows"]:
                row["uid"] = officer["uid"]
                rowdict = {k: row[k] for k in fields}
                w.writerow(rowdict)
