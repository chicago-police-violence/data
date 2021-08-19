import csv
from openpyxl import load_workbook
import xlrd
from itertools import islice
import datetime
import os
import logging
import zipfile

logging.basicConfig(
    format="%(levelname)s:%(message)s",
    level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper()),
)


def flatten_stars(officer):
    officer["stars"] = tuple(officer["star" + str(i)] for i in range(1, 11))
    return officer


def convert_race(s):
    race_dict = {
        "S": "WHITE HISPANIC",
        "BLK": "BLACK",
        "WHI": "WHITE",
        "API": "ASIAN/PACIFIC ISLANDER",
        "WBH": "BLACK HISPANIC",
        "WWH": "WHITE HISPANIC",
        "I": "AMER IND/ALASKAN NATIVE",
        "U": "",
        "": "",
        None: "",
    }
    return race_dict[s]


def parse_cell(cell):
    if cell.ctype == 0:
        return None
    elif cell.ctype == 1:
        return "" if cell.value.startswith("----") else cell.value
    elif cell.ctype == 2:
        return float(cell.value)
    elif cell.ctype == 3:
        if not cell.value:
            return None
        else:
            return datetime.datetime(*xlrd.xldate.xldate_as_tuple(cell.value, 0))


def to_int(a):
    return None if (a is None or a == "") else int(a)


def parse_date(date):
    # cannot use standard strptime function from the standard library for two
    # reasons:
    # - non standard month names
    # - two digit year number some of which are before 1969 which is the pivot
    #   year in the standard library
    if not date:
        return None
    months = [
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    ]
    day, month, year = date.split("-")
    day = int(day)
    month = months.index(month) + 1
    year = int(year) + (2000 if int(year) < 19 else 1900)
    return datetime.date(year, month, day)


def parse_miltime(time):
    # parse military time integer, e.g. 1456 becomes time 02:56 PM
    return None if not time else datetime.time(*divmod(time, 100))


def get_date(datetime):
    return None if datetime is None else datetime.date()

def get_award_datetime(s):
    if (not s) or (s == ""):
        return None

    # special cases to fix data entry errors
    # replacement dates inferred from other entries
    if s == "17-AUG-1012 00:00:00":
        return datetime.date(2012, 8, 17)
    if s == "15-AUG-0201 00:00:00":
        return datetime.date(2016, 8, 15)
    if s == "24-JUL-0201 00:00:00":
        return datetime.date(2014, 7, 24)
    if s == "31-MAY-0200 00:00:00":
        return datetime.date(2009, 5, 31)
    if s == "04-MAR-0200 00:00:00":
        return datetime.date(2009, 3, 4)

    if ":" in s:
        return datetime.datetime.strptime(s, "%m/%d/%Y %H:%M")
    else:
        return datetime.datetime.strptime(s, "%m/%d/%Y")

def csv_read(filename, use_dict=True, skip=0):
    fh = open(filename)
    reader = csv.DictReader(fh) if use_dict else csv.reader(fh)
    return islice(reader, skip, None)

def zipped_csv_read(filename, use_dict=True, skip=0):
    with zipfile.ZipFile(filename, mode='r') as zf:
        zf.extractall(os.path.dirname(filename))
    csv_name = os.path.splitext(filename)[0]+'.csv'
    ret = csv_read(csv_name, use_dict, skip)
    os.remove(csv_name)
    return ret

def xlsx_read(file_name, sheet_name, skip=1,reset=False):
    wb = load_workbook(filename=file_name, read_only=True)
    ws = wb[sheet_name]
    if reset:
        ws.reset_dimensions()
    return islice(ws.values, skip, None)


def xls_read(file_name, sheet_name, skip=1):
    wb = xlrd.open_workbook(file_name)
    rows = wb.sheet_by_name(sheet_name).get_rows()
    for row in islice(rows, skip, None):
        yield list(map(parse_cell, row))

def sanitize(d, rules):
    for keys, function in rules:
        for key in keys:
            d[key] = function(d[key])


def process(rows, output_file, field_names, rules):
    # wrapper around csv.DictWriter which cleans each dictionary according to
    # some rules before writing it
    with open(output_file, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        for row in rows:
            assert len(row) == len(field_names), f"len(row) = {len(row)} and len(fieldnames) = {len(field_names)}; row is {row}"
            row_dict = dict(zip(field_names, row))
            sanitize(row_dict, rules)
            writer.writerow(row_dict)
