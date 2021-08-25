from utils import csv_read
from collections import defaultdict
from datetime import date
from csv import DictWriter


def parse_date(d):
    return None if d == "" else date.fromisoformat(d)


def print_history(history, o):
    for i, e in enumerate(history):
        e["start"] = parse_date(e["start_date"])
        e["end"] = parse_date(e["end_date"])
        if i == 0:
            units = [row["unit_no"] for row in profiles[e["uid"]] if row["unit_no"]]
            print(
                f"=== {e['uid']} ({o['appointment_date']}, {o['resignation_date']}) {units} {o['birthyear']} ==="
            )
        if e["unit_no"] != "":
            print("{:3d}".format(int(e["unit_no"])), e["start"], e["end"])
        else:
            print("{:3d}".format(0), e["start"], e["end"])


def fix(history, app):

    for e in history:

        if e["end"] is not None and e["start"] > e["end"]:
            # e is a bogus entry with start date later than end date let us try
            # to find another entry to help us fix it once we find a fix, we
            # set e["unit_no"] = "" as a way to flag it is fixed by another
            # entry so that it is not included in the end
            for ep in history:
                if (
                    ep["unit_no"] == e["unit_no"]
                    and e["start"] == ep["start"]
                    and (ep["end"] is None or ep["end"] > e["end"])
                ):
                    # we can find another row with same unit and start date so
                    # most likely explanation, there was a double entry on that
                    # day, and we simply ignore the one with impossible end date.
                    #
                    # 6129 officers
                    e["unit_no"] = ""
                    break
                if (
                    (e["start"] - e["end"]).days == 1
                    and ep["start"] == e["start"]
                    and (ep["end"] is None or ep["end"] > ep["start"])
                ):
                    # end date is just one day before start date, but we can
                    # find another entry with same start date and different
                    # unit number. Quite likely, the other entry was
                    # a correction to the first one which automatically filled
                    # in the end date of the wrong one, so we also ignore the
                    # wrong one
                    #
                    # 247 officers
                    e["unit_no"] = ""
                    break
                if ((ep["start"] - e["end"]).days == 1) and (
                    ep["end"] is None or ep["end"] > e["start"]
                ):
                    # we can find another entry `ep` which starts one day after
                    # the end of the current faulty entry `e`. So the faulty
                    # end date in `e` was automatically generated from `ep`.
                    if e["start"] == app and ep["start"] < app:
                        # this happens when the officer had assignments before
                        # his appointment date (probably was employed by the
                        # CPD before becoming an officer).
                        #
                        # In this case the faulty entry comes from their first
                        # assignment as an officer (typically the police
                        # academy), but the rest of the entries form
                        # a chronological linear history.
                        e["end"] = ep["end"]
                        break
                    if len(history) == 2:
                        e["unit_no"] = ""
                        break
                    else:
                        ep["start"] = e["start"]
                        e["unit_no"] = ""
                        break
            else:
                e["unit_no"] = ""

    return [e for e in history if e["unit_no"] != ""]

def process(history):
    o = roster[history[0]["uid"]]
    app = parse_date(o["appointment_date"])
    res = parse_date(o["resignation_date"])

    cleaned = []

    for e in history:
        if e["unit_no"] == "":
            continue
        e["start"] = parse_date(e["start_date"])
        e["end"] = parse_date(e["end_date"])
        if e["start"] is None:
            e["start"] = app
        if res is not None and e["start"] > res:
            if e["start"] == date(1990, 1, 1) and e["end"] is None:
                if len(history) == 1:
                    e["start"] = app
                    e["end"] = res
        cleaned.append(e)

    cleaned.sort(key=lambda e: e["start"])

    for i, e in enumerate(cleaned):
        if e["end"] is not None and e["start"] > e["end"]:
            break
        if i > 0 and (cleaned[i-1]["end"] is None or (e["start"] - cleaned[i-1]["end"]).days != 1):
            break
    else:
        return cleaned

    return fix(cleaned, app)

if __name__ == "__main__":
    from sys import argv, exit

    roster = dict()
    for row in csv_read(argv[2]):
        roster[row["uid"]] = row

    # maps officer uid to list of assignments for this officer
    officers = defaultdict(list)
    for row in csv_read(argv[1]):
        officers[row["uid"]].append(row)

    with open(argv[1], "w") as fh:
        fields = ["uid", "unit_no", "start_date", "end_date"]
        hw = DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        hw.writeheader()
        for history in officers.values():
            cleaned = process(history)
            for e in cleaned:
                e["start_date"] = e["start"]
                e["end_date"] = e["end"]
                hw.writerow(e)

