import sys
import os.path
import utils
from parse_p046957 import get_accused

basename = os.path.basename(sys.argv[1])

if basename == "P0-46360_main.csv":
    rows = utils.xlsx_read(sys.argv[2], "Sheet1")
    fields = [
        "trr_id",
        "rd_no",
        "cr_no_obtained",
        "subject_cb_no",
        "event_no",
        "beat",
        "block",
        "street_direction",
        "street_name",
        "location",
        "date",
        "time",
        "indoor_or_outdoor",
        "lighting_condition",
        "weather_condition",
        "notify_oemc",
        "notify_dist_sergeant",
        "notify_op_command",
        "notify_det_div",
        "number_of_weapons_discharged",
        "party_fired_first",
        "last_name",
        "first_name",
        "gender",
        "race",
        "age",
        "appointment_date",
        "unit_no",
        "unit_detail",
        "assigned_beat",
        "rank",
        "duty_status",
        "injured",
        "member_in_uniform",
        "subject_gender",
        "subject_race",
        "subject_age",
        "subject_birthyear",
        "subject_armed",
        "subject_injured",
        "subject_alleged_injury",
    ]
    rules = [
        (["date", "appointment_date"], utils.get_date),
        (["time"], utils.parse_miltime),
    ]
elif basename == "P0-46360_discharges.csv":
    rows = utils.xlsx_read(sys.argv[2], "WeaponDischarges")
    fields = [
        "trr_id",
        "weapon_type",
        "weapon_type_descr",
        "firearm_make",
        "firearm_model",
        "firearm_barrel_length",
        "firearm_caliber",
        "total_number_of_shots",
        "firearm_reloaded",
        "number_of_catdridge_reloaded",
        "handgun_worn_type",
        "handgun_drawn_type",
        "method_used_to_reload",
        "sight_used",
        "protective_cover_used",
        "discharge_distance",
        "object_struck_of_discharge",
        "discharge_position",
    ]
    rules = []
elif basename == "P0-46360_stars.csv":
    rows = utils.xlsx_read(sys.argv[2], "Star #")
    fields = ["trr_id", "last_name", "first_name", "star"]
    rules = []
elif basename == "P0-46360_members.csv":
    rows = utils.xlsx_read(sys.argv[2], "Statuses_OtherMembers")
    fields = [
        "trr_id",
        "status",
        "datetime",
        "first_name",
        "last_name",
        "star",
        "rank",
        "gender",
        "race",
        "age",
        "appointment_date",
    ]
    rules = [(["appointment_date"], utils.get_date)]
elif basename == "16-1105.csv":
    rows = utils.xlsx_read(sys.argv[2], "Sheet1")
    fields = [
        "last_name",
        "first_name",
        "gender",
        "race",
        "age",
        "appointment_date",
        "unit_no",
        "start_date",
        "end_date",
    ] + ["star" + str(i) for i in range(1, 11)]
    rules = [(["appointment_date", "start_date", "end_date"], utils.get_date)]
elif basename == "P4-41436.csv":
    rows = utils.xlsx_read(sys.argv[2], "Export Worksheet")
    fields = [
        "first_name",
        "last_name",
        "middle_initial",
        "gender",
        "race",
        "age",
        "sworn",
        "appointment_date",
        "position_no",
        "unit_id",
        "unit_no",
        "unit_detail",
        "resignation_date",
        "star",
    ]
    rules = [
        (["appointment_date", "resignation_date"], utils.parse_date),
        (["race"], utils.convert_race),
    ]
elif basename == "P0-52262.csv":
    rows = utils.xlsx_read(sys.argv[2], "Sheet2")
    fields = [
        "last_name",
        "first_name",
        "middle_initial",
        "gender",
        "race",
        "birthyear",
        "appointment_date",
        "unit_no",
        "start_date",
        "end_date",
    ]
    rules = [(["appointment_date", "start_date", "end_date"], utils.get_date)]
elif basename == "P0-58155.csv":
    rows = utils.xlsx_read(sys.argv[2], "Sheet1")
    fields = [
        "last_name",
        "first_name",
        "middle_initial",
        "gender",
        "race",
        "birthyear",
        "age",
        "status",
        "appointment_date",
        "position_no",
        "position_description",
        "unit_no",
        "unit_description",
        "resignation_date",
    ] + ["star" + str(i) for i in range(1, 12)]

    rules = [(["appointment_date", "resignation_date"], utils.get_date)]
elif basename == "18-060-425_main.csv":
    rows = utils.csv_read(sys.argv[2], use_dict=False, skip=1)
    fields = [
        "complaint_no",
        "incident_start",
        "incident_end",
        "complaint_date",
        "closed_date",
        "status",
        "location_code",
        "street_no",
        "street_direction",
        "street_name",
        "apt_no",
        "city",
        "state",
        "zip_code",
        "beat",
        "category_code",
        "category_description",
        "category_type",
        "shooting",
        "complainant_type",
        "investigating_agency",
    ]
    rules = [
        (
            ["incident_start", "incident_end", "complaint_date", "closed_date"],
            utils.parse_date,
        )
    ]
elif basename == "18-060-425_accused.csv":
    rows = utils.csv_read(sys.argv[2], use_dict=False, skip=1)
    fields = [
        "complaint_no",
        "first_name",
        "last_name",
        "middle_initial",
        "race",
        "gender",
        "birthyear",
        "star",
        "employee_no",
        "position_description",
        "allegation_category",
        "allegation_category_code",
        "investigation_category",
        "investigation_category_code",
        "position_description_1",
        "assigned_unit",
        "detail_unit",
        "arrested",
        "on_duty",
        "injury_condition",
        "finding_code",
        "finding_narrative",
        "accusation_id",
        "penalty_id",
        "penalty_code",
        "no_of_days",
        "narrative",
        "iad_ops",
        "cr_required",
    ]
    rules = [(["race"], utils.convert_race)]
elif basename == "P0-46957_accused.csv":
    rows = get_accused(sys.argv[2])
    fields = [
        "complaint_no",
        "name",
        "birthyear",
        "gender",
        "race",
        "appointment_date",
        "unit",
        "rank",
        "star",
        "complaint_category",
        "finding",
        "discipline",
        "final_finding",
        "final_discipline",
    ]
    rules = [
        (["appointment_date"], utils.get_date),
        (["complaint_no", "birthyear", "star"], utils.to_int),
        (["race"], utils.convert_race),
    ]

utils.process(rows, sys.argv[1], fields, rules)
