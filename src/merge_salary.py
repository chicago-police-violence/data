from utils import csv_read, multi_csv_read, flatten_stars
from uuid import uuid4
from matcher import Matcher
from csv import DictWriter
from datasets import datasets
from collections import defaultdict
import os.path


#def comp_age(officer1, officer2):
#    birthyear = int(officer2018 - int(officer2["age"])
#    return int(officer1["birthyear"]) in [birthyear, birthyear - 1]

def flatten_salary(records, id_attributes):
    officers = defaultdict(list)
    for record in records:
        key = tuple(record[k] for k in id_attributes)
        officers[key].append(record)
    for key, records in officers.items():
        years = [record['salary_year'] for record in records]
        if len(set(years)) != len(years):
            print(f"Warning: multiple salary records for a year found")
            print(records)
        #assert len(set(years)) == len(years), f"officer salary record contains duplicate years, {records}"
        salary_history = {}
        for record in records:
            salary_history[record['salary_year']] = {k : v for k, v in record.items() if k not in id_attributes and k != 'salary_year'}
        officer = {k : v for k, v in record.items() if k in id_attributes}
        officer['salary_history'] = salary_history
        yield officer


def f1(officer, m):
    if len(officers := m[officer]) >= 1:
        unique_uids = set([officer['uid'] for officer in officers])
        if len(unique_uids) > 1:
            print(f"Warning: matched to multiple officers\n Officer: {officer} \n Officers: {officers}")
        return officers[0]["uid"]

f1.key = ["first_name", "last_name", "middle_initial", "appointment_date"]


if __name__ == "__main__":
    from sys import argv

    profiles = csv_read(argv[2])
    m = Matcher(flatten_stars(profile) for profile in profiles)

    basename, _ = os.path.splitext(os.path.basename(argv[3]))
    salary_records = multi_csv_read(argv[3:6])
    flattened_salary_records = flatten_salary(salary_records, datasets[basename]["id_fields"])

    linked, unlinked = m.match(flattened_salary_records, [f1])

    d1, _ = os.path.splitext(os.path.basename(argv[2]))
    d2, _ = os.path.splitext(os.path.basename(argv[3]))

    profiles = list(m.unify(linked, unlinked, matcher_source='profiles', matchee_source='salary'))

    fields = datasets["P0-58155"]["fields"]
    fields += [f for f in datasets["P4-41436"]["fields"] if f not in fields]
    fields += ["source", "uid"]

    with open(argv[2], "w") as fh:
        writer = DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for officer in sorted(
            m.unify(linked, unlinked, d1, d2),
            key=lambda l: (l["last_name"], l["first_name"], l["uid"]),
        ):
            writer.writerow(officer)

    with open(argv[2], "w") as pf:
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
