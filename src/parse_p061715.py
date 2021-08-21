import csv

def main(fn):
    # split the REQUESTER field into two fields: REQ_LNM, REQ_FNM
    rows = []
    with open(fn, 'r') as f:
        reader = csv.DictReader(f) 
        for row in reader:
            req_nm = row.pop('REQUESTER')
            names = [s.strip() for s in req_nm.split(',')]
            assert len(names) == 2, f"requester name was not in the format (last name), (first name): {req_nm}"
            row['REQ_LNM'] = names[0]
            row['REQ_FNM'] = names[1]
            rows.append(row)
    with open(fn, 'w') as f:
        writer = csv.DictWriter(f, rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
