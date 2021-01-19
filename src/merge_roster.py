from utils import csv_read, flatten_stars
from uuid import uuid4
from set_matcher import Matcher
from csv import DictWriter
from datasets import datasets
import os.path


def comp_age(officer1, officer2):
    birthyear = 2018 - int(officer2["age"])
    return int(officer1["birthyear"]) in [birthyear, birthyear - 1]


def f1(officer, m):
    if officer["sworn"] == "N" or officer["appointment_date"] > "2017-04-17":
        # the first roster does not contain unsworn officers (see response letter) or
        # officers hired after 2017-04-17 since it was received on that day
        return uuid4()
    if len(officers := m[officer]) == 1:
        return officers[0]["uid"]
    elif len(officers) > 1:
        for o in officers:
            if officer["star"] != "" and officer["star"] in o["stars"]:
                return o["uid"]


f1.key = ["first_name", "last_name", "middle_initial", "appointment_date"]


def f2(officer, m):
    for o in m[officer]:
        if officer["star"] == "" or officer["star"] not in o["stars"]:
            continue
        if not comp_age(o, officer):
            continue
        if all(
            officer[k] == o[k]
            for k in ["first_name", "gender", "race", "middle_initial"]
        ):
            # change of last name (marriage or divorce)
            return o["uid"]
        elif any(officer[k] == o[k] for k in ["first_name", "last_name"]):
            # by visual inspections this covers obvious typo fixes
            # and the case of Megan Woods, the only CPD transgender officer:
            # https://www.nbcchicago.com/news/chicago-police-department-transgender-officer1/2295602/
            return o["uid"]


f2.key = ["appointment_date"]


def f3(officer, m):
    for o in m[officer]:
        if comp_age(o, officer):
            # those were missed before because the officer's current star
            # does not appear in the first roster
            return o["uid"]


f3.key = ["first_name", "last_name", "appointment_date"]
# f3.debug = True


def f4(officer, m):
    if len(officers := m[officer]) == 1:
        o = officers[0]
        if comp_age(o, officer) and o["middle_initial"] == officer["middle_initial"]:
            # a couple additional change of last names that weren't caught
            # earlier since the officer's current star does not appear in the
            # first roster
            return o["uid"]


f4.key = ["first_name", "appointment_date"]
# f4.debug = True


if __name__ == "__main__":
    from sys import argv

    m = Matcher(
        flatten_stars(o)
        for o in csv_read(argv[1])
        if o["last_name"] not in ["", "Officer", "OFFICER"]
    )

    officers = filter(lambda o: o["last_name"], csv_read(argv[2]))
    linked, unlinked = m.match(officers, [f1, f2, f3, f4])

    d1, _ = os.path.splitext(os.path.basename(argv[1]))
    d2, _ = os.path.splitext(os.path.basename(argv[2]))
    fields = datasets[d1]["fields"]
    fields += [f for f in datasets[d2]["fields"] if f not in fields]
    fields += ["source", "uid"]

    with open(argv[3], "w") as fh:
        writer = DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for officer in sorted(
            m.unify(linked, unlinked, d1, d2),
            key=lambda l: (l["last_name"], l["first_name"], l["uid"]),
        ):
            writer.writerow(officer)
