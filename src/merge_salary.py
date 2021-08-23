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
# within these groupings, we check last name, middle init, age, officer_date, appointment_date, present_posn_start_date
# if apt_date is missing, fill in with officer_date
# compute birthyear_apt and birthyear_off 
# if last name agrees: MI must agree or be missing, one of apt date / officer date must agree (cross links possible), and birthyear must be within 1y (cross link possible)
# if last name doesn't agree: MI must agree or be missing, apt date and birthyear_apt must agree

def record_matches_list(rec, li):
    for lr in li:
        # if middle initial exists in both, they must match
        if rec['middle_initial'] != '' and lr['middle_initial'] != '' and rec['middle_initial'] != lr['middle_initial']:
            return False
        # birthyear is a bit unreliable (it can often jump by about 10 years, especially in the records for 2016,2017...)
        # so as long as we get a strong match on other attributes, birthyear can vary; otherwise, it can't (only 1y allowed)

        # option 1: MI exists and matches, appointment date and officer date both exist & match (not necessarily different)
        # option 2: MI soft matches (might be missing), appointment date and officer date both match and are different (unique info like this implies good match)
        # then BY not necessary to check
        # otherwise, BY must be within 1Y
        mi_hard_match = rec['middle_initial'] != '' and rec['middle_initial'] == lr['middle_initial']
        mi_soft_match = (rec['middle_initial'] == '') or (lr['middle_initial'] == '') or (rec['middle_initial'] == lr['middle_initial'])
        apt_hard_match = rec['appointment_date'] != '' and rec['appointment_date'] == lr['appointment_date']
        off_hard_match = rec['officer_date'] != '' and rec['officer_date'] == lr['officer_date']
        apt_off_diff = rec['officer_date'] != rec['appointment_date']
        if not ((mi_hard_match and apt_hard_match and off_hard_match) or (mi_soft_match and apt_hard_match and off_hard_match and apt_off_diff)):
            if rec['birthyear'] != '' and lr['birthyear'] != '' and abs(int(rec['birthyear']) - int(lr['birthyear'])) > 1:
                return False
    #passed all checks, so match
    return True

def flatten_salary(records, id_attributes):

    # match on first name and gender (there will of course be multiple officers in each group, this is very coarse)
    flatten_attributes = ['last_name', 'first_name', 'appointment_date']
    officers = defaultdict(list)
    for record in records:
        # fill in appointment date with officer date if apt date is missing
        if record['appointment_date'] == '':
            record['appointment_date'] = record['officer_date']
        # compute birthyear (up to 1 year)
        record['birthyear'] = '' if (record['appointment_date'] == '' or record['age_hire'] == '') else str(datetime.strptime(record['appointment_date'], '%Y-%m-%d').year - int(record['age_hire']))
        key = tuple(record[k] for k in flatten_attributes)
        officers[key].append(record)

    # now we split these groupings by using more fine-grained rules
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
        # sometimes this splits an officer into two. We can fix the majority of these by seeing whether there are mutually disjoint salary years
        if len(unq_officers) == 2:
            years0 = [rec['year'] for rec in unq_officers[0]]
            years1 = [rec['year'] for rec in unq_officers[1]]
            if len(years0) + len(years1) == len(set(years0 + years1)):
                unq_officers = [unq_officers[0]+unq_officers[1]]
        _officers.extend(unq_officers)
    officers = _officers
            
    # find officers where there are multiple same-year entries with the same position and put out a warning
    for recs in officers:
        year_posns = defaultdict(list)
        for rec in recs:
            year_posns[rec['year']].append(rec['position_description'])
        for year, posns in year_posns.items():
            if len(set(posns)) != len(posns):
                print(f"Warning: single officer has multiple records for same posn in same year\n{recs[0]['last_name'], recs[0]['first_name'], recs[0]['middle_initial'], recs[0]['birthyear']}")
                break
        
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
        off = {}
        off['salary_history'] = salary_history
        for attr in id_attributes + ['birthyear']:
            attrvals = set([rec[attr] for rec in officer])
            attrvals.discard('')
            off[attr] = '' if len(attrvals) == 0 else list(attrvals)[0]
        yield off

# TODO handle the multiple matches case properly
# match on full name and apt date
def f1(officer, m):
    if len(officers := m[officer]) >= 1:
        unique_uids = set([off['uid'] for off in officers])
        if len(unique_uids) > 1:
            print(f"Warning: matched to multiple officers:\n Officers: {set([(off['first_name'], off['last_name'], off['uid']) for off in officers])}")
        return officers[0]["uid"]

f1.key = ["first_name", "last_name", "middle_initial", "appointment_date"]


# match on name and apt date (but force MI to match, or MI to soft match and age to match)
def f2(officer, m):
    if len(officers := m[officer]) >= 1:
        unique_uids = set([off['uid'] for off in officers])
        if len(unique_uids) > 1:
            print(f"Warning: matched to multiple officers:\n Officers: {set([(off['first_name'], off['last_name'], off['uid']) for off in officers])}")
        off1 = officer
        mi1 = off1['middle_initial']
        by1 = off1['birthyear']
        for off2 in officers:
            mi2 = off2['middle_initial']
            by2 = off2['birthyear']
            if mi1 != '' and mi1.strip() == mi2.strip():
                return off2["uid"]
            if by1 != '' and by2 != '' and abs(int(by1)-int(by2)) < 2 and (mi1 == '' or mi2 == '' or mi1.strip() == mi2.strip()):
                return off2["uid"]

f2.key = ["first_name", "last_name", "appointment_date"]


def normalize_name(name):
    # replace special characters with whitespace, and compress whitespaces
    name = (''.join([ch if ch.isalpha() else ' ' for ch in name])).strip()
    name = ' '.join(name.split())
    # remove suffix
    suffixes = [' JR', ' SR', ' II', ' III', ' IV']
    namesuff = ''
    for suff in suffixes:
        if name[-len(suff):] == suff:
            namesuff = suff
            name = name[:-len(suff)]
            break
    # normalize the main name
    name = ''.join([ch for ch in name if ch.isalpha()])
    return name, namesuff

# match on first name and appointment date, then normalize lastname (because these two DBs differ), then apply f2
def f3(officer, m):
    ln, lsuff = normalize_name(officer['last_name'])
    submatches = []
    for off in m[officer]:
        # extract normalized last name
        ln2, lsuff2 = normalize_name(off['last_name'])
        # if suffix soft matches, and last name hard matches, add this officer to the submatch list
        # otherwise (e.g. if one is JR and the other is SR) no match
        if ln != '' and ln == ln2 and (lsuff == '' or lsuff2 == '' or lsuff == lsuff2):
            submatches.append(off)
    # now essentially run f2
    if len(submatches) >= 1:
        unique_uids = set([off['uid'] for off in submatches])
        if len(unique_uids) > 1:
            print(f"Warning: matched to multiple officers:\n Officers: {set([(off['first_name'], off['last_name'], off['uid']) for off in submatches])}")
        off1 = officer
        mi1 = off1['middle_initial']
        by1 = off1['birthyear']
        for off2 in submatches:
            mi2 = off2['middle_initial']
            by2 = off2['birthyear']
            if mi1 != '' and mi1.strip() == mi2.strip():
                return off2["uid"]
            if by1 != '' and by2 != '' and abs(int(by1)-int(by2)) < 2 and (mi1 == '' or mi2 == '' or mi1.strip() == mi2.strip()):
                return off2["uid"]

f3.key = ["first_name", "appointment_date"]

def f4(officer, m):
    if len(officers := m[officer]) >= 1:
        unique_uids = set([off['uid'] for off in officers])
        if len(unique_uids) > 1:
            # if multiple matches on this (weak) key, just ignore
            return
        off1 = officer
        mi1 = off1['middle_initial']
        by1 = off1['birthyear']
        for off2 in officers:
            mi2 = off2['middle_initial']
            by2 = off2['birthyear']
            if mi1 != '' and mi2 != '' and by1 != '' and by2 != '' and abs(int(by1) - int(by2)) < 2:
                return off2["uid"]
f4.key = ["first_name", "middle_initial", "appointment_date"]

if __name__ == "__main__":
    from sys import argv

    profiles = csv_read(argv[2])

    basename, _ = os.path.splitext(os.path.basename(argv[3]))
    salary_records = multi_csv_read(argv[3:6])
    salary_flat = flatten_salary(salary_records, datasets[basename]["id_fields"])

    m = Matcher(profiles)
    linked, unlinked = m.match(salary_flat, [f1, f2, f3, f4])

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
        fields = ["uid","year","salary","position_description","pay_grade","present_posn_start_date","officer_date", "employee_status"]
        salary_fields = ["year","salary","position_description","pay_grade","present_posn_start_date", "employee_status"]
        sw = DictWriter(sf, fieldnames=fields, extrasaction="ignore")
        sw.writeheader()
        for profile in profiles:
            if 'salary_history' in profile:
                sorted_years = sorted([year for year in profile["salary_history"]])
                for year in sorted_years:
                    for record in profile["salary_history"][year]:
                        row = dict([('uid', profile['uid']), ("officer_date", profile["officer_date"])] + [(key, record[key]) for key in salary_fields]) 
                        sw.writerow(row)
