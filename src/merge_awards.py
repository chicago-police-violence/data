from utils import csv_read
from uuid import uuid4
from matcher import Matcher
from csv import DictWriter
from datasets import datasets
from collections import defaultdict
import os.path
from datetime import datetime


#def comp_age(officer1, officer2):
#    birthyear = int(officer2018 - int(officer2["age"])
#    return int(officer1["birthyear"]) in [birthyear, birthyear - 1]

# check if a record matches a list of other records
# it does not match if there is a conflict in Age or MI (if they exist)
def record_matches_list(rec, li):
    for lr in li:
        if rec['middle_initial'] != '' and lr['middle_initial'] != '' and rec['middle_initial'] != lr['middle_initial']:
            return False
        if rec['age_appointment'] != '' and lr['age_appointment'] != '' and abs(int(rec['age_appointment']) - int(lr['age_appointment'])) > 1:
            return False
    return True

def flatten_salary(records, id_attributes):
    
    # match on name and start date (there will be multiple officers in each group, this is very coarse)
    # if start date as city emp is missing, fill it in with appt date (it's more complete than appt date in this database since this db has civilians)
    flatten_attributes = ['first_name', 'last_name', 'appointment_date']
    officers = defaultdict(list)
    for record in records:
        key = tuple((record[k] if (record[k] != '' or k != 'appointment_date') else record['officer_date']) for k in flatten_attributes)
        officers[key].append(record)

    # now within these groupings, consider a match if (MI nonempty + matches) or if age is within 1 year
    _officers = []
    for key, recs in officers.items():
        unq_officers = []
        for rec in recs:
            found = False
            for unqo in unq_officers:
                if record_matches_list(rec, unqo):
                    unqo.append(rec)
                    found = True
                    break
            if not found:
                unq_officers.append([rec])
        _officers.extend(unq_officers)
    officers = _officers
            
    # find officers where there are multiple same-year entries with the same position and put out a warning
    for recs in officers:
        year_posns = defaultdict(list)
        for rec in recs:
            year_posns[rec['year']].append(rec['title'])
        for year, posns in year_posns.items():
            if len(set(posns)) != len(posns):
                print(f"\nWarning: single officer has multiple records for same posn in same year\n{recs}\n\n")
        
    # there are some officers with multiple records in one year
    # this happens when their position changes
    # there is one case where an officer changes more than once in a year (MICHAEL CHIOCCA in 2015)
    # there is one case where the salary changes immediately (JAMES ROUSSELL in 2014)
    # so we will sort the records within a year by start date at present position
    for officer in officers:
        salary_history = defaultdict(list)
        for record in officer:
            salary_history[record['year']].append({k : v for k, v in record.items() if k not in id_attributes})
        for year in salary_history:
            salary_history[year] = sorted(salary_history[year], key=lambda ll : ll['present_posn_start_date'])
        off = {k : v for k, v in record.items() if k in id_attributes}
        off['salary_history'] = salary_history
        yield off

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

def merge_rows(iterators, fields):
    for iterator in iterators:
        for row in iterator:
            for field in fields:
                if field not in row:
                    row[field] = ''
            yield row

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

    #with open(argv[1], "w") as sf:
    #    fields = ["uid","year","salary","title","pay_grade","present_posn_start_date","officer_date", "employee_status"]
    #    salary_fields = ["year","salary","title","pay_grade","present_posn_start_date", "employee_status"]
    #    sw = DictWriter(sf, fieldnames=fields, extrasaction="ignore")
    #    sw.writeheader()
    #    for profile in profiles:
    #        if 'salary_history' in profile:
    #            sorted_years = sorted([year for year in profile["salary_history"]])
    #            for year in sorted_years:
    #                for record in profile["salary_history"][year]:
    #                    row = dict([('uid', profile['uid']), ("officer_date", profile["officer_date"])] + [(key, record[key]) for key in salary_fields]) 
    #                    sw.writerow(row)
