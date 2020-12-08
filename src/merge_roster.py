from utils import csv_read, flatten_stars
from uuid import uuid4
from matcher import Matcher
from csv import DictWriter
from itertools import chain


def comp_age(officer1, officer2):
    birthyear = 2018 - int(officer2["age"])
    return int(officer1["birthyear"]) in [birthyear, birthyear - 1]


def f1(officer, m):
    if officer["sworn"] == "N" or officer["appointment_date"] > "2017-04-17":
        # the first roster does not contain unsworn officers (see response letter) or
        # officers hired after 2017-04-17 since it was received on that day
        officer["uid"] = uuid4()
        return
    if len(officers := m[officer]) == 1:
        return officers[0]
    elif len(officers) > 1:
        for o in officers:
            if officer["star"] != "" and officer["star"] in o["stars"]:
                return o


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
            return o
        elif any(officer[k] == o[k] for k in ["first_name", "last_name"]):
            # by visual inspections this covers obvious typo fixes
            # and the case of Megan Woods, the only CPD transgender officer:
            # https://www.nbcchicago.com/news/chicago-police-department-transgender-officer1/2295602/
            return o


f2.key = ["appointment_date"]


def f3(officer, m):
    for o in m[officer]:
        if comp_age(o, officer):
            # those were missed before because the officer's current star
            # does not appear in the first roster
            return o


f3.key = ["first_name", "last_name", "appointment_date"]
# f3.debug = True


def f4(officer, m):
    if len(officers := m[officer]) == 1:
        o = officers[0]
        if comp_age(o, officer) and o["middle_initial"] == officer["middle_initial"]:
            # a couple additional change of last names that weren't caught
            # earlier since the officer's current star does not appear in the
            # first roster
            return o


f4.key = ["first_name", "appointment_date"]
# f4.debug = True


if __name__ == "__main__":
    import sys

    m = Matcher()
    for officer in csv_read(sys.argv[1]):
        if officer["last_name"] not in ["", "Officer", "OFFICER"]:
            m.add(flatten_stars(officer))

    officers = filter(lambda o: o["last_name"], csv_read(sys.argv[2]))
    linked, unlinked = m.match(officers, [f1, f2, f3, f4])

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

    def get_officers():
        for officer in chain(m, m.removed()):
            officer["source"] = "P0-58155"
            yield officer
        for officer in linked:
            officer["source"] = "P4-41436"
            yield officer
        for officer in unlinked:
            officer["source"] = "P4-41436"
            officer["uid"] = uuid4()
            yield officer

    with open("linked/profiles.csv", "w") as fh:
        writer = DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for officer in sorted(
            get_officers(), key=lambda l: (l["last_name"], l["first_name"], l["uid"])
        ):
            writer.writerow(officer)