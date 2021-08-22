from utils import csv_read, multi_csv_read
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

f1.key = ["first_name", "last_name", "middle_initial", "appointment_date"]


# match on name and apt date (but allow either age or MI match)
def f2(officer, m):
    if len(officers := m[officer]) >= 1:
        unique_uids = set([officer['uid'] for officer in officers])
        if len(unique_uids) > 1:
            print(f"Warning: matched to multiple officers:\n Officers: {set([(officer['first_name'], officer['last_name'], officer['uid']) for officer in officers])}")
        off1 = officer
        mi1 = off1['middle_initial']
        by1 = None
        try:
            by1 = datetime.strptime(off1['appointment_date'], '%Y-%m-%d').year - int(off1['age_appointment'])
        except:
            pass
        off2 = officers[0]
        mi2 = off2['middle_initial']
        by2 = None
        for _o2 in officers:
            try:
                by2 = int(_o2['birthyear'])
            except:
                pass
        if mi1.strip() == mi2.strip():
            return off2["uid"]
        if by1 and by2 and abs(by1-by2) < 2:
            return off2["uid"]

f2.key = ["first_name", "last_name", "appointment_date"]

# match on just name (but pick the entry that matches the most of apt date, MI, and age)
# there will be quite a few muti-uid matches here
def f3(officer, m):
    if len(officers := m[officer]) >= 1:
        off1 = officer
        mi1 = off1['middle_initial']
        ad1 = off1['appointment_date'] if off1['appointment_date'] != '' else off1['officer_date']
        by1 = None
        try:
            by1 = datetime.strptime(off1['appointment_date'], '%Y-%m-%d').year - int(off1['age_appointment'])
        except:
            pass
        maxscore = 0
        bestoff2 = None
        for off2 in officers:
            mi2 = off2['middle_initial']
            by2 = None
            for _o2 in officers:
                try:
                    by2 = int(_o2['birthyear'])
                except:
                    pass
            ad2 = off2['appointment_date']
            score = (mi1.strip() == mi2.strip()) + (ad1 == ad2)
            if by1 and by2 and abs(by2-by1) < 2:
                score += 1
            if score > maxscore:
                maxscore = score
                bestoff2 = off2
        if bestoff2:
            #print(f"\n\nMATCH3:\n{officer}\n{bestoff2}\n\n")
            return bestoff2['uid']
f3.key = ["first_name", "last_name"]


# match on just one name + apt date, and match as long as there is only one UID so far in the cleaning
# (there are a bunch of misspellings of names in the HR data...)
def f4(officer, m):
    if len(officers := m[officer]) >= 1:
        unique_uids = set([officer['uid'] for officer in officers])
        if len(unique_uids) == 1:
            print(f"\n\nMATCH3:\n{officer}\n{officers[0]}\n\n")
            if officer['middle_initial'] != '' and officers[0]['middle_initial'] != '' and officer['middle_initial'] != officers[0]['middle_initial']:
                print(f"\n\nBADMATCH3:\n{officer}\n{officers[0]}\n\n")
            return officers[0]['uid']
f4.key = ["last_name", "appointment_date"]

#
#def f4(officer, m):
#    if len(officers := m[officer]) >= 1:
#        unique_uids = set([officer['uid'] for officer in officers])
#        if len(unique_uids) == 1:
#            print(f"\n\nMATCH4:\n{officer}\n{officers[0]}\n\n")
#            if officer['middle_initial'] != '' and officers[0]['middle_initial'] != '' and officer['middle_initial'] != officers[0]['middle_initial']:
#                print(f"\n\nBADMATCH4:\n{officer}\n{officers[0]}\n\n")
#            return officers[0]['uid']
#f4.key = ["first_name", "appointment_date"]

if __name__ == "__main__":
    from sys import argv

    profiles = csv_read(argv[2])

    basename, _ = os.path.splitext(os.path.basename(argv[3]))
    salary_records = multi_csv_read(argv[3:6])
    salary_flat = flatten_salary(salary_records, datasets[basename]["id_fields"])


    # code that merges entries using a more coarse matcher
    # shows officers that get split up by the above very fine-grained flattening
    # so that you can visually inspect splits to make sure they are sensible
    # this code block is just for visually debugging the flattening, so commented out.
    #offs = defaultdict(list)
    #for ff in salary_flat:
    #    key = (ff['last_name'], ff['first_name'], ff['gender'], ff['age_appointment'])
    #    offs[key].append(ff)

    #for key, off in offs.items():
    #    if len(off) > 1:
    #        print()
    #        print('KEY')
    #        print(key)
    #        for li in off:
    #            print('ITEM')
    #            print((li['last_name'], li['first_name'], li['middle_initial'], li['gender'], li['appointment_date'], li['age_appointment'], li['officer_date']))
    #        print()
    #quit()


    m = Matcher(profiles)
    linked, unlinked = m.match(flattened_salary_records, [f1, f2, f3])

    profiles = sorted(
            m.unify(linked, unlinked, matchee_source='salary'),
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

    with open(argv[1], "w") as sf:
        fields = ["uid","year","salary","title","pay_grade","present_posn_start_date","officer_date", "employee_status"]
        salary_fields = ["year","salary","title","pay_grade","present_posn_start_date", "employee_status"]
        sw = DictWriter(sf, fieldnames=fields, extrasaction="ignore")
        sw.writeheader()
        for profile in profiles:
            if 'salary_history' in profile:
                sorted_years = sorted([year for year in profile["salary_history"]])
                for year in sorted_years:
                    for record in profile["salary_history"][year]:
                        row = dict([('uid', profile['uid']), ("officer_date", profile["officer_date"])] + [(key, record[key]) for key in salary_fields]) 
                        sw.writerow(row)
