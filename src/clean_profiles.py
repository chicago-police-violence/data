from utils import csv_read
from collections import defaultdict
from datasets import datasets
from sys import argv
from csv import DictWriter

def key(c):
    d = {    
        "P0-58155": 2,
        "P4-41436": 1,
        "P0-52262": 3,
        "16-1105": 4,
        "P0-46957_accused": 5,
        "P0-46360_main": 6,
        }
    return d[c[0]]


if __name__ == "__main__":
    officers = defaultdict(list)
    for profile in csv_read(argv[1]):
        officers[profile["uid"]].append(profile)

    fields = datasets["P0-58155"]["fields"]
    fields += [f for f in datasets["P4-41436"]["fields"] if f not in fields]
    fields += ["uid"]
    

    with open(argv[2], "w") as pf:
        w = DictWriter(pf, fieldnames=fields, extrasaction="ignore")
        w.writeheader()

        for uid, profiles in officers.items():
            row = {}
            for f in fields:
                candidates = [(p["source"], p[f]) for p in profiles if p[f] not in ["", "UNKNOWN"]]
                if candidates:
                    candidates.sort(key=key)
                    row[f] = candidates[0][1]
                else:
                    row[f] = ""
            w.writerow(row)
