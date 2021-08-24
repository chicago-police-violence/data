from utils import csv_read
from matcher import Matcher
from collections import defaultdict
from uuid import uuid4
from csv import DictWriter
from datasets import datasets, write_profiles


def before(old, new):
    # tests whether `old` as an assignement history is a prefix of `new` that
    # is, `new` contains all the assignements in `old` (possibly adding an end
    # date to the last one) and possibly more.
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
        # officers appointed after the second release,
        # so they con't be present in the first release
        return uuid4()
    for o in (officers := m[officer]) :
        if comp_age(officer, o) and before(o, officer):
            return o["uid"]
    else:
        if officer["history"] == sorted(
            (e for o in officers for e in o["history"]), key=lambda e: e[1]
        ):
            # we can't find a match with a single officer, but this officer's
            # assignement history is equal to the concatenation of the
            # assignement histories of all his potential matches, so we "split"
            # this officer.

            # handles the case of SMTIH, ROBERT
            return [{**officer, "history": o["history"], "uid": o["uid"]} for o in officers]

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
    import link_history

    s1, s2 = "16-1105", "P0-52262" # old dataset, new dataset

    # first we merge the two history datasets together
    officers = flatten_history(csv_read(argv[2]), datasets[s1]["id_fields"])
    m = Matcher(officers)
    officers = flatten_history(csv_read(argv[3]), datasets[s2]["id_fields"])
    linked, unlinked = m.match(officers, [f1, f2, f3])

    # next we build the list of officer profiles found in the history datasets.
    # for all uids which match between the two datasets we have two profiles
    # so `officers` maps a uid to one or two profiles
    officers = defaultdict(list)
    for o in m.unify(linked, unlinked, s1, s2):
        officers[o["uid"]].append(o)
        del o["uid"] # del uid since we are going to match against `profiles.csv`

    # link the profiles from history datasets to the profiles in `profiles.csv`
    profiles = link_history.link(officers.values(), argv[-2])
    write_profiles(argv[-2], profiles)

    with open(argv[1], "w") as hf:
        fields = ["uid", "unit_no", "start_date", "end_date"]
        hw = DictWriter(hf, fieldnames=fields, extrasaction="ignore")
        hw.writeheader()
        for profiles in officers.values():
            # we keep the assignment history from the latest dataset
            p = None
            for pr in profiles:
                if pr["source"] == "P0-52262":
                    p = pr
                    break
            else:
                p = profiles[0]
            for e in p["history"]:
                hw.writerow(dict(zip(fields, [p["uid"]] + list(e))))
