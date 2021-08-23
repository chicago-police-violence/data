from collections import defaultdict
from itertools import chain
from utils import csv_read
import csv
import sys

def clean_name(name):
    if name is not None:
        name = " ".join(name.split())
    replace = {
            "TRAFFIC SECTION DETAIL UNIT": "DETAIL UNIT",
            "BOMB AND ARSON DIVISION": "ARSON SECTION",
            "BUREAU OF STAFF SERVICES": "TECHNOLOGY AND RECORDS GROUP",
            "BUREAU OF ORGANIZATIONAL DEVELOPMENT": "TECHNOLOGY AND RECORDS GROUP",
            "FORENSIC SERVICES UNIT - ET NORTH": "FORENSIC SERVICES UNIT ET NORTH",
            "ASSET FORFEITURE INVESTIGATION SECTION": "ASSET FORFEITURE SECTION",
            "CRIME CONTROL STRATEGIES SECTION": "OFFICE OF CRIME CONTROL STRATEGIES",
            "PROP CRIMES DDA 2": "PROP CRIMES DDA2",
            "ASST SUPERINTENDENT-LAW ENFORCEMENT OPERATIONS": "ASST SUPERINTENDENT - LAW ENFORCEMENT OPERATIONS",
            "OEMC - DETAIL SECTION": "OEC - DETAIL SECTION",
            "COMMUNITY RELATIONS DIVISION": "CHICAGO ALTERNATIVE POLICING STRATEGY (CAPS) DIVISION",
            "TROUBLED BUILDING UNIT": "TROUBLED BUILDING SECTION",
            "": None,
            "UNKNOWN": None,
            }
    return replace.get(name, name)

def collect_units(datasets):
    # collect all units appearing in all datasets other than the reference dataset
    units = defaultdict(set)
    for row in chain(*map(csv_read, datasets)):
        if row['unit_no'] != '':
            try:
                unit_no = int(row['unit_no'])
            except ValueError:
                # this only happens for WALKER, NOREEN in P0-46957_accused.csv with
                # unit 'PA2' but the unit assignement hisotry of this officer
                # reveals they were part of unit 177 for their entire career so we
                # ignore
                continue
        desc = clean_name(row.get('unit_description'))
        if desc is not None:
            units[unit_no].add(desc)
        elif unit_no not in units:
            units[unit_no] = set()
    return units

def load_reference(reference):
    reference_units = defaultdict(list)
    for row in csv_read(reference):
        unit_no = int(row['unit_no'])
        row['unit_no'] = unit_no
        if row['unit_description'] in ['', 'UNKNOWN']:
            row['unit_description'] = None
        reference_units[unit_no].append(row)
    return reference_units

def main(output, datasets, reference):
    units = collect_units(datasets)
    reference_units = load_reference(reference)


    final = list()
    for unit_no, descs in units.items():
        refs = reference_units[unit_no]
        if unit_no == 138:
            descs.add("FIELD MONITORING UNIT")
        if unit_no == 153:
            final.append({'unit_no': '153b', 'unit_description': 'SPECIAL FUNCTIONS SUPPORT UNIT', 'active_status': 'Y', 'status_date': '2016-05-06'})
            final.append({'unit_no': '153a', 'unit_description': 'MOBILE STRIKE FORCE', 'active_status': 'N', 'status_date': '2016-05-06'})
            continue

        assert(len(descs) <= 1)
        if len(descs) == 0:
            assert(len(refs) <= 1)
            if len(refs) == 0:
                final.append({'unit_no': unit_no})
            elif len(refs) == 1:
                final.append(refs[0])
        elif len(descs) == 1:
            desc = descs.pop()
            for ref in refs:
                if ref['unit_description'] == desc:
                    final.append(ref)
                    break
            else:
                final.append({'unit_no': unit_no, 'unit_description': desc})
        elif len(descs) > 1:
            print(unit_no, descs)

    field_names = ['unit_no', 'unit_description', 'active_status', 'status_date']
    with open(output, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        final.sort(key=lambda x: x['unit_no'] if isinstance(x['unit_no'],int) else 153)
        for row in final:
            writer.writerow(row)

if __name__ == "__main__":
    output = sys.argv[1]
    reference = sys.argv[2]
    datasets = sys.argv[3:-1]

    main(output, datasets, reference)
