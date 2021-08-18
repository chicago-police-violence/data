from csv import DictWriter
from itertools import chain
from utils import get_date, sanitize, xls_read
import os.path

keys = [
    "complaint_no",
    "beat",
    "location_code",
    "street_no",
    "street_name",
    "apt_no",
    "city",
    "incident_datetime",
    "complaint_date",
    "closed_date",
]

investigator_keys = [
    "complaint_no",
    "name",
    "assignment",
    "rank",
    "star",
    "appointment_date",
]

complaint_files = {
    "p046957_-_report_1.1_-_all_complaints_in_time_frame.xls": 10,
    "p046957_-_report_1.2_-_all_complaints_in_time_frame.xls": 9,
    "p046957_-_report_1.3_-_all_complaints_in_time_frame.xls": 9,
    "p046957_-_report_1.5_-_all_complaints_in_time_frame.xls": 8,
    "p046957_-_report_1.6_-_all_complaints_in_time_frame.xls": 9,
}


def read_complaint_file(input_file, skip):
    cur_comp_no = None
    for row in xls_read(input_file, "Sheet1", skip):
        if row[0] is not None:
            row = row[:10]
            assert len(row) == len(keys)
            row_dict = dict(zip(keys, row))
            sanitize(
                row_dict,
                [
                    (["complaint_no"], int),
                    (["complaint_date", "closed_date"], get_date),
                ],
            )
            cur_comp_no = row_dict["complaint_no"]
            yield row_dict
        elif row[1] == "Investigator/Assignment/Rank/Star/Appt Date:":
            row = [cur_comp_no] + row[2:7]
            assert len(row) == len(investigator_keys)
            row_dict = dict(zip(investigator_keys, row))
            sanitize(row_dict, [(["appointment_date"], get_date)])
            yield row_dict


def get_complaints(directory):
    return chain.from_iterable(
        read_complaint_file(os.path.join(directory, f), skip)
        for f, skip in complaint_files.items()
    )


def main(input_dir, output_dir):
    main_fn = os.path.join(output_dir, "P0-46957_main.csv")
    inv_fn = os.path.join(output_dir, "P0-46957_investigators.csv")
    with open(main_fn, "w") as comp_csv, open(inv_fn, "w") as inv_csv:
        comp_writer = DictWriter(comp_csv, fieldnames=keys)
        comp_writer.writeheader()
        inv_writer = DictWriter(inv_csv, fieldnames=investigator_keys)
        inv_writer.writeheader()
        for row_dict in get_complaints(input_dir):
            writer = inv_writer if "name" in row_dict else comp_writer
            writer.writerow(row_dict)


accused_files = {
    "p046957_-_report_2.1_-_identified_accused.xls": 11,
    "p046957_-_report_2.2_-_identified_accused.xls": 11,
    "p046957_-_report_2.3_-_identified_accused.xls": 10,
    "p046957_-_report_2.4_-_identified_accused.xls": 10,
    "p046957_-_report_2.5_-_identified_accused.xls": 11,
}


def read_accused_file(input_file, skip):
    cur_comp_no = None
    for row in xls_read(input_file, "Sheet1", skip):
        if row[0]:
            cur_comp_no = row[0]
        elif row[2]:
            row = [cur_comp_no] + row[2:5] + row[6:16]
            yield row


def get_accused(directory):
    return chain.from_iterable(
        read_accused_file(os.path.join(directory, f), skip)
        for f, skip in accused_files.items()
    )


if __name__ == "__main__":
    import sys

    main(sys.argv[2], sys.argv[1])
