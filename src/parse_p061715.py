import csv

def main(fn):
    # split the REQUESTER field into two fields: REQ_LNM, REQ_FNM
    # split the RANK field into two fields: POSITION_NO and POSITION_DESC
    rows = []
    with open(fn, 'r') as f:
        reader = csv.DictReader(f) 
        for row in reader:
            req_nm = row.pop('REQUESTER')
            names = [s.strip() for s in req_nm.split(',')]
            assert len(names) == 2, f"REQUESTER was not in the format (last name), (first name): {req_nm}"
            row['REQ_LNM'] = names[0]
            row['REQ_FNM'] = names[1]

            posn = row.pop('RANK')
            if posn == 'UNK-UNKNOWN':
                row['POSITION_NO'] = ''
                row['POSITION_DESC'] = ''
            else:
                assert posn[4] == '-' and int(posn[:4]), f"RANK was not in the format (position #)-(position name): {posn}"
                row['POSITION_NO'] = posn[:4]
                row['POSITION_DESC'] = posn[5:]
            rows.append(row)

    with open(fn, 'w') as f:
        writer = csv.DictWriter(f, rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
