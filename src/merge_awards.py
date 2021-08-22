from utils import csv_read
from uuid import uuid4
from matcher import Matcher
from csv import DictWriter
from datasets import datasets
from collections import defaultdict
import os.path
from datetime import datetime


# TODO handle the multiple matches case properly
# match on full name and apt date
def f1(officer, m):
    if len(officers := m[officer]) >= 1:
        unique_uids = set([officer['uid'] for officer in officers])
        if len(unique_uids) > 1:
            print(f"Warning: matched to multiple officers:\n Officers: {set([(officer['first_name'], officer['last_name'], officer['uid']) for officer in officers])}")
        return officers[0]["uid"]

f1.key = ["first_name", "last_name", "birthyear", "appointment_date", "gender", "race"]

def flatten_awards(records, id_attributes):
    officers = defaultdict(list)
    for record in records:
        # this flattening procedure is very conservative (requires a very fine-grained match)
        # and in particular, there are cases where middle initial actually helps disambiguate 
        # (e.g. there are two JAMES BANSLEYs that are identical up to MI, but correspond to two officers per salary data)
        # however, there are cases where MI is missing in some records but not in others -- the flatten procedure would erroneously create multiple separate entries for these
        # so instead here we fill in the MI for the small number of special cases by visual inspection using the (independent) salary data 
        # MARQUITA CROSBY does not appear in salary. But she also doesn't appear anywhere else, and all of her records have 
        # exactly 2 duplicates -- one with mid initial C, one with missing entry. Award ref numbers and tracking numbers are all identical. So merge these too.
        # I have verified by inspection that with the below 4 fixes, even though it's quite conservative, this procedure overall makes no obviously erroneous splits of officers
        if record['first_name'] == 'AUDREY' and record['last_name'] == 'JURCZYKOWSKI':
            record['middle_initial'] = 'A'
        if record['first_name'] == 'ERICK' and record['last_name'] == 'VON KONDRAT':
            record['middle_initial'] = 'M'
        if record['first_name'] == 'STEPHEN' and record['last_name'] == 'MYTHEN':
            record['middle_initial'] = 'C'
        if record['first_name'] == 'MARQUITA' and record['last_name'] == 'CROSBY':
            record['middle_initial'] = 'C'
       
        key = tuple(record[k] for k in id_attributes)
        officers[key].append(record)
    for key, awards in officers.items():
        officer = dict(zip(id_attributes, key))
        officer["awards"] = sorted(awards, key=lambda e: e['award_request_date'])
        yield officer

if __name__ == "__main__":
    from sys import argv


    # get flattened versions of both awards files
    p061715 = csv_read(argv[3])
    s1, _ = os.path.splitext(os.path.basename(argv[3]))
    p061715_flat = flatten_awards(p061715, datasets[s1]['id_fields'])

    p506887 = csv_read(argv[4])
    s2, _ = os.path.splitext(os.path.basename(argv[4]))
    p506887_flat = flatten_awards(p506887, datasets[s2]['id_fields'])

    print('Matching p061715')
    # create profile matcher and link to p061715
    profiles = csv_read(argv[2])
    m = Matcher(profiles)
    linked, unlinked = m.match(p061715_flat, [f1])
    profiles = sorted(
            m.unify(linked, unlinked, matchee_source=s1),
            key=lambda l: (l["last_name"], l["first_name"], str(l["uid"])),
        )

    print('Matching p506887')
    # create profile matcher and link to p061715
    # create second profile matcher using new profiles and link to p506887
    m = Matcher(profiles)
    linked, unlinked = m.match(p506887_flat, [f1])
    profiles = sorted(
            m.unify(linked, unlinked, matchee_source=s2),
            key=lambda l: (l["last_name"], l["first_name"], str(l["uid"])),
        )

    pfields = datasets["P0-58155"]["fields"]
    pfields += [f for f in datasets["P4-41436"]["fields"] if f not in pfields]
    pfields += ["source", "uid"]

    with open(argv[2], "w") as fp:
        writer = DictWriter(fp, fieldnames=pfields, extrasaction="ignore")
        writer.writeheader()
        for officer in profiles:
            writer.writerow(officer)

    with open(argv[1], "w") as af:
        fields = ["uid", "award_request_date",  "award_ref_number", "award_type", "requester_last_name", "requester_first_name", "requester_middle_initial", "tracking_no", "current_status", "incident_start_date", "incident_end_date", "incident_description", "ceremony_date"]
        award_fields = fields[1:]
        aw = DictWriter(af, fieldnames=fields, extrasaction="ignore")
        aw.writeheader()
        for profile in profiles:
            if 'awards' in profile:
                awards = sorted(profile['awards'], key = lambda ll : ll['award_request_date'])
                for award in awards:
                    # since we have two awards files with not identical field names, insert explicit missing entries where necessary
                    row = dict([('uid', profile['uid'])] + [(key, award[key] if key in award else '') for key in award_fields]) 
                    aw.writerow(row)
