import networkx as nx
import csv
from collections import defaultdict
from itertools import combinations
import os.path as op

DATA_DIR = "../final/"

def csv_read(filename):
    with open(filename) as fh:
        yield from csv.DictReader(fh)

def build_complaint_graph():
    complaints_officers = defaultdict(set) # maps a complain_no to set of officers
    for row in csv_read(op.join(DATA_DIR, "complaints_officers.csv")):
        complaints_officers[row["complaint_no"]].add(row["uid"])

    g = nx.Graph()
    for complaint_no, officers in complaints_officers.items():
        for pair in combinations(officers,2):
            g.add_edge(*pair)
    return g

if __name__ == "__main__":
    g = build_complaint_graph()
    print(f"Complaints graph: {len(g)} officers, {g.size()} edges")

    # load roster and print information of highest degree node
    roster = {row["uid"]: row for row in csv_read(op.join(DATA_DIR, "roster.csv"))}
    node, degree = max(g.degree(), key=lambda x: x[1])
    print(f"Max degree node: {roster[node]}")
