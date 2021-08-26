from utils import csv_read
from uuid import uuid4
from matcher import Matcher
from csv import DictWriter
from datasets import datasets
from collections import defaultdict
import os.path
from datetime import datetime


# TODO handle the multiple matches case properly
# match on everything available
def f1(officer, m):
    if len(officers := m[officer]) >= 1:
        unique_uids = set([off['uid'] for off in officers])
        if len(unique_uids) > 1:
            print(f"Warning: matched to multiple officers:\n Officers: {set([(off['first_name'], off['last_name'], off['uid']) for off in officers])}")
        return officers[0]["uid"]

f1.key = ["first_name", "last_name", "middle_initial", "birthyear", "appointment_date", "gender", "race"]

# TODO handle the multiple matches case properly
# match on everything except middle initial
def f2(officer, m):
    if len(officers := m[officer]) >= 1:
        unique_uids = set([off['uid'] for off in officers])
        if len(unique_uids) > 1:
            print(f"Warning: matched to multiple officers:\n Officers: {set([(off['first_name'], off['last_name'], off['uid']) for off in officers])}")
        return officers[0]["uid"]

f2.key = ["first_name", "last_name", "birthyear", "appointment_date", "gender", "race"]

# TODO handle the multiple matches case properly
# match on name/dates/gender (remove race -- e.g. a lot of "WHITE HISPANIC" from other data is just "HISPANIC" here)
def f3(officer, m):
    if len(officers := m[officer]) >= 1:
        unique_uids = set([off['uid'] for off in officers])
        if len(unique_uids) > 1:
            print(f"Warning: matched to multiple officers:\n Officers: {set([(off['first_name'], off['last_name'], off['uid']) for off in officers])}")
        return officers[0]["uid"]

f3.key = ["first_name", "last_name", "birthyear", "appointment_date", "gender"]

# match on name / appointment star, and at least one of star or apt date must exist
# must only be one match and at least one of star or appointment must exist
def f4(officer, m):
    if len(officers := m[officer]) >= 1:
        unique_uids = set([off['uid'] for off in officers])
        if len(unique_uids) == 1:
            for off in officers:
                if off['star'] != '' or off['appointment_date'] != '':
                    return officers[0]['uid']

f4.key = ["first_name", "last_name", "appointment_date", "star"]

# match on name and star (star must exist)
def f5(officer, m):
    if len(officers := m[officer]) >= 1:
        unique_uids = set([off['uid'] for off in officers])
        if len(unique_uids) == 1:
            for off in officers:
                if off['star'] != '':
                    return officers[0]['uid']

f5.key = ["first_name", "last_name", "star"]

# match on name and star (star must exist)
def f6(officer, m):
    if len(officers := m[officer]) >= 1:
        unique_uids = set([off['uid'] for off in officers])
        if len(unique_uids) == 1:
            for off in officers:
                if off['appointment_date'] != '':
                    return officers[0]['uid']

f6.key = ["first_name", "last_name", "appointment_date"]

# match on name / appointment star, and at least one of star or apt date must exist
# must only be one match and at least one of star or appointment must exist
def f7(officer, m):
    for off in (officers := m[officer]):
        if off['star'] != '' and (off['first_name'] == officer['first_name'] or off['last_name'] == officer['last_name']):
            return off['uid']

f7.key = ["star"]

def f8(officer, m):
    for off in (officers := m[officer]):
        if off['appointment_date'] != '':
            return off['uid']
f8.key = ["last_name", "appointment_date", "race"]



def flatten_awards(records, id_attributes):
    officers = defaultdict(list)
    for record in records:
        # this flattening procedure is very conservative (requires a very fine-grained match)
        # however, there are cases where data is missing in some records but not in others -- the flatten procedure would erroneously create multiple separate entries for these
        # so instead here we fix a few officers' entries by visual inspection, using the other data sources + salary to verify that these are uniquely identifiable
        if record['first_name'] == 'AUDREY' and record['last_name'] == 'JURCZYKOWSKI':
            record['middle_initial'] = 'A'
        if record['first_name'] == 'ERICK' and record['last_name'] == 'VON KONDRAT':
            record['middle_initial'] = 'M'
        if record['first_name'] == 'STEPHEN' and record['last_name'] == 'MYTHEN':
            record['middle_initial'] = 'C'
        if record['first_name'] == 'MARQUITA' and record['last_name'] == 'CROSBY':
            record['middle_initial'] = 'C'
        if record['first_name'] == "HERBERT" and record['last_name'] == 'KORDECK':
            record['middle_initial'] = 'C'
            record['birthyear'] = '1936' 
            record['gender'] = 'M'
            record['race'] = 'WHTIE'
            record['appointment_date'] = '1962-02-26'
            record['resignation_date'] = '1990-06-08' 
        if record['first_name'] == 'THOMAS' and record['last_name'] == 'SLAD':
            record['appointment_date'] = '1997-07-07'
        if record['first_name'] == 'VINCENT' and record['last_name'] == 'BROWN':
            record['appointment_date'] = '2007-04-02'
        if record['first_name'] == 'EDDIE' and record['last_name'] == 'YOSHIMURA':
            record['birthyear'] = '1957'
        if record['first_name'] == 'GARY' and record['last_name'] == 'LORDEN':
            record['middle_initial'] = 'E'
            record['star'] = '11893'
            record['appointment_date'] = '1993-11-22'
        if record['first_name'] == 'SILVIA' and record['last_name'] == 'LOPEZ':
            record['birthyear'] = '1960'
            record['race'] = 'HISPANIC'
           
       
        key = tuple(record[k] for k in id_attributes)
        officers[key].append(record)
    for key, awards in officers.items():
        officer = dict(zip(id_attributes, key))
        officer["awards"] = sorted(awards, key=lambda e: e['award_request_date'])
        # replace the star entries that were unused in flattening 
        # since multiple stars may exist over time, use the star1 star2 star3 ... entries
        # ordered by award request date
        # fill in the "star" entry with the officer's final recorded star number 
        stars = [award["star"] for award in officer["awards"] if award["star"] != ""]
        # get unique star numbers preserving order
        seen = set()
        stars = [st for st in stars if not (st in seen or seen.add(st))] 
        assert len(stars) < 11, f"Officer has more than 11 star numbers on record; out of room in profiles.\nKEY:\n{key}\nSTARS:\n{stars}\nRECORDS\n{awards}"
        for i in range(11):
            if i < len(stars):
                officer[f"star{i+1}"] = stars[i]
            else:
                officer[f"star{i+1}"] = ""
        officer["star"] = "" if len(stars) == 0 else stars[-1]
        # same thing for position_no and description: fill in with latest entry
        posns = [(award["position_no"], award["position_description"]) for award in officer["awards"] if "position_no" in award and award["position_no"] != ""]
        officer["position_no"] = "" if len(posns) == 0 else posns[-1][0]
        officer["position_description"] = "" if len(posns) == 0 else posns[-1][1]

        yield officer

if __name__ == "__main__":
    from sys import argv

    # Note: we will only link for UIDs that exist at this point. Awards data
    # will not create new UIDs / profiles because the officer demographic info
    # here is less reliable and will require more careful cleaning/flattening/linking.
    # In a future version, we will allow  awards records to add new UIDs to the pool.

    # get flattened versions of both awards files
    p061715 = csv_read(argv[2])
    s1, _ = os.path.splitext(os.path.basename(argv[2]))
    p061715_flat = flatten_awards(p061715, datasets[s1]['id_fields'])

    p506887 = csv_read(argv[3])
    s2, _ = os.path.splitext(os.path.basename(argv[3]))
    p506887_flat = flatten_awards(p506887, datasets[s2]['id_fields'])

    # get erroneous UIDs identified in earlier stages
    with open(argv[-3], 'r') as erf:
        erroneous_uids = [e.strip() for e in erf.readlines()]

    print('Matching p061715')
    # create profile matcher and link to p061715 (remove erroneous UIDs to avoid matching confusion)
    profiles = list(csv_read(argv[-2]))
    # realize the iterator and split into good/erroneous
    original_uids = [prof['uid'] for prof in profiles]
    good_profiles = [prof for prof in profiles if prof['uid'] not in erroneous_uids]
    err_profiles = [prof for prof in profiles if prof['uid'] in erroneous_uids]
    m = Matcher(good_profiles)
    linked, unlinked = m.match(p061715_flat, [f1, f2, f3, f4, f5, f6, f7, f8])
    profiles = sorted(
            m.unify(linked, unlinked, matchee_source=s1),
            key=lambda l: (l["last_name"], l["first_name"], str(l["uid"])),
        )

    print('Matching p506887')
    # create profile matcher and link to p061715
    # create second profile matcher using new profiles and link to p506887
    m = Matcher(profiles)
    linked, unlinked = m.match(p506887_flat, [f1, f2, f3, f4, f5, f6, f7, f8])
    profiles = sorted(
            list(m.unify(linked, unlinked, matchee_source=s2)) + err_profiles,
            key=lambda l: (l["last_name"], l["first_name"], str(l["uid"])),
        )

    pfields = datasets["P0-58155"]["fields"]
    pfields += [f for f in datasets["P4-41436"]["fields"] if f not in pfields]
    pfields += ["source", "uid"]

    with open(argv[-2], "w") as fp:
        writer = DictWriter(fp, fieldnames=pfields, extrasaction="ignore")
        writer.writeheader()
        for officer in profiles:
            # TODO this line prevents awards from creating new profile entries
            # TODO once we allow awards to generate new UIDs/profile entries, remove this if statement
            if 'awards' not in officer:
                writer.writerow(officer)

    with open(argv[1], "w") as af:
        fields = ["uid", "star", "position_no", "position_description", "award_request_date",  "award_ref_number", "award_type", "requester_last_name", "requester_first_name", "requester_middle_initial", "tracking_no", "current_status", "incident_start_date", "incident_end_date", "incident_description", "ceremony_date"]
        award_fields = fields[1:]
        aw = DictWriter(af, fieldnames=fields, extrasaction="ignore")
        aw.writeheader()
        for profile in profiles:
            # TODO the second part of this if statement prevents awards from storing info about new UIDs (restricted to original UIDs)
            # TODO once we allow awards to generate new UIDs/profile entries, remove the second clause in this if statement
            if 'awards' in profile and profile['uid'] in original_uids:
                awards = sorted(profile['awards'], key = lambda ll : ll['award_request_date'])
                for award in awards:
                    # since we have two awards files with not identical field names, insert explicit missing entries where necessary
                    row = dict([('uid', profile['uid'])] + [(key, award[key] if key in award else '') for key in award_fields]) 
                    aw.writerow(row)
