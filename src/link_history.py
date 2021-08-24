from matcher import Matcher
from utils import csv_read, flatten_stars


def f1(officer, m):
    if (
        len(s := set(u["uid"] for o in officer if "middle_initial" in o for u in m[o]))
        == 1
    ):
        return s.pop()


f1.key = [
    "first_name",
    "last_name",
    "race",
    "gender",
    "appointment_date",
    "middle_initial",
]


def f2(officer, m):
    s = set(u["uid"] for o in officer if "star1" in o for u in m[flatten_stars(o)])
    if len(s) == 1:
        return s.pop()


f2.key = ["stars", "appointment_date"]
# f2.debug = True


def f3(officer, m):
    if len(s := set(u["uid"] for o in officer if "birthyear" in o for u in m[o])) == 1:
        return s.pop()


f3.key = ["last_name", "appointment_date", "birthyear"]
# f4.debug = True

f4 = lambda o, m: f3(o, m)
f4.key = ["first_name", "last_name", "birthyear"]
# f4.debug = True

f5 = lambda o, m: f3(o, m)
f5.key = ["first_name", "appointment_date", "birthyear"]
# f5.debug = True


def link(officers, profiles_file):
    from sys import argv

    m = Matcher(flatten_stars(profile) for profile in csv_read(profiles_file))
    linked, unlinked = m.match(officers, [f1, f2, f1, f3, f4, f5])
    return list(m.unify(linked, unlinked))
