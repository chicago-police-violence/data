from utils import csv_read, flatten_stars
from collections import defaultdict
from csv import writer
import sys

if __name__ == "__main__":

    erroneous_uids = set()

    # load profiles
    key_attrs = ["first_name", "last_name", "appointment_date"]
    officers = defaultdict(list)
    for row in csv_read(sys.argv[2]):
        row = flatten_stars(row)
        key = tuple(row[k] for k in key_attrs)
        officers[key].append(row)

    assignments = defaultdict(list)
    for assignment in csv_read(sys.argv[3]):
        if assignment["unit_no"]:
            assignments[assignment["uid"]].append(assignment)


    for key, profiles in officers.items():
        uids = list(set(profile["uid"] for profile in profiles))

        # these are possibly ambiguous profiles so we need to check whether
        # these are actually different individuals, or if one is a "ghost",
        # inactive entry which should be flagged
        if len(uids) > 1:

            assert(len(uids) == 2) # thankfully we never have to deal with more than two uids

            dicts = {"birthyear": dict(), "middle_initial": dict()}
            for k, d in dicts.items():
                for profile in profiles:
                    if profile[k]:
                        d[profile["uid"]] = profile[k]

            # we first check whether the different uids correspond to different
            # birthyears, in which case we are fairly confident these are
            # different invididuals and nothing needs to be done.
            birthyears = list(map(int, dicts["birthyear"].values()))
            if len(birthyears) == len(uids):
                if max(birthyears) - min(birthyears) > 0:
                    continue
            
            # we can disambiguate based on middle initial, so these are different
            # individuals
            initials = set(dicts["middle_initial"].values())
            if len(initials) == len(uids):
                continue

            uids.sort(key=lambda x: len(assignments[x]))
            if len(assignments[uids[0]]) <= 1 and len(assignments[uids[1]]) >= 2:
                # the uid with empty or single assignment is the "inactive" one" one
                erroneous_uids.add(uids[0])
                #print(key)
                continue
            
            # we now have three officers:
            # - ROBERT SMITH who is clearly two different individuals, with
            #   different stars and assignments
            # - KEVIN SHANLEY and JOHN ISHAQ who only show up in P4-41436 with
            #   different ages, so we are assuming they correspond to two
            #   different individuals each

    with open(sys.argv[1], "w") as fh:
        w = writer(fh)
        for uid in erroneous_uids:
            w.writerow([uid]) 

