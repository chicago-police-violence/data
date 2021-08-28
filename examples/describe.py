import csv
import sys
from collections import defaultdict
from os.path import basename

if __name__ == "__main__":

    with open(sys.argv[1]) as file:
        rdr = csv.DictReader(file)
        ctrs = {attr: defaultdict(int) for attr in rdr.fieldnames}
        miss = {attr: 0 for attr in rdr.fieldnames}
        cnt = 0
        for record in rdr:
            cnt += 1
            for attr in rdr.fieldnames:
                if record[attr] == "":
                    miss[attr] += 1
                else:
                    ctrs[attr][record[attr]] += 1

    pct = lambda n: f"{100*n:.3g}%"
    fmt = lambda values: ", ".join(f"`{v[0]}` ({pct(v[1]/cnt)})" for v in values)

    print(f"### `{basename(sys.argv[1])}` ({cnt} records)\n")
    print("| Field | Description | Values | Missing |\n| --- | --- | --- | --- |")
    for attr, ctr in ctrs.items():
        values = sorted(ctr.items(), key=lambda x: x[1], reverse=True)
        values = values[:10]
        print(f"| `{attr}` | | {fmt(values)} | {pct(miss[attr]/cnt)} |")
