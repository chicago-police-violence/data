import networkx as nx
import csv
from collections import defaultdict
from itertools import combinations
import os.path as op

DATA_DIR = "../final/"

def csv_read(filename):
    with open(op.join(DATA_DIR,filename)) as fh:
        yield from csv.DictReader(fh)

def build_complaint_graph():
    # build a dictionary mapping a complaint_no to set of UIDs of officers
    # listed in the complaint
    complaints_officers = defaultdict(set)
    for row in csv_read("complaints_officers.csv"):
        complaints_officers[row["complaint_no"]].add(row["uid"])

    g = nx.Graph()
    for complaint_no, officers in complaints_officers.items():
        # add an edge for each pair of officers appearing in a given complaint
        for pair in combinations(officers,2):
            g.add_edge(*pair)
    return g

if __name__ == "__main__":
    g = build_complaint_graph()
    print(f"Complaints graph: {len(g)} officers, {g.size()} edges")

    # load roster and print information of highest degree node
    roster = {row["uid"]: row for row in csv_read("roster.csv")}
    node, degree = max(g.degree(), key=lambda x: x[1])
    print(f"Max degree node: {roster[node]}")
