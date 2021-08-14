import utils
from parse_p046957 import get_accused

datasets = {
    "P0-46360_main": {
        "rows": lambda fn: utils.xlsx_read(fn, "Sheet1"),
        "fields": [
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
        ],
        "id_fields": [
            "last_name",
            "first_name",
            "gender",
            "race",
            "appointment_date",
        ],
        "rules": [
            (["date", "appointment_date"], utils.get_date),
            (["time"], utils.parse_miltime),
        ],
    },
    "P0-46360_discharges": {
        "rows": lambda fn: utils.xlsx_read(fn, "WeaponDischarges"),
        "fields": [
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
        ],
        "rules": [],
    },
    "P0-46360_stars": {
        "rows": lambda fn: utils.xlsx_read(fn, "Star #"),
        "fields": ["trr_id", "last_name", "first_name", "star"],
        "rules": [],
    },
    "P0-46360_members": {
        "rows": lambda fn: utils.xlsx_read(fn, "Statuses_OtherMembers"),
        "fields": [
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
        ],
        "rules": [(["appointment_date"], utils.get_date)],
    },
    "16-1105": {
        "rows": lambda fn: utils.xlsx_read(fn, "Sheet1"),
        "fields": [
            "last_name",
            "first_name",
            "gender",
            "race",
            "age",
            "appointment_date",
            "unit_no",
            "start_date",
            "end_date",
        ]
        + ["star" + str(i) for i in range(1, 11)],
        "id_fields": [
            "last_name",
            "first_name",
            "gender",
            "race",
            "age",
            "appointment_date",
        ]
        + ["star" + str(i) for i in range(1, 11)],
        "rules": [(["appointment_date", "start_date", "end_date"], utils.get_date)],
    },
    "P4-41436": {
        "rows": lambda fn: utils.xlsx_read(fn, "Export Worksheet"),
        "fields": [
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
        ],
        "rules": [
            (["appointment_date", "resignation_date"], utils.parse_date),
            (["race"], utils.convert_race),
        ],
    },
    "P0-52262": {
        "rows": lambda fn: utils.xlsx_read(fn, "Sheet2"),
        "fields": [
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
        ],
        "id_fields": [
            "last_name",
            "first_name",
            "gender",
            "race",
            "appointment_date",
            "middle_initial",
            "birthyear",
        ],
        "rules": [(["appointment_date", "start_date", "end_date"], utils.get_date)],
    },
    "P0-58155": {
        "rows": lambda fn: utils.xlsx_read(fn, "Sheet1"),
        "fields": [
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
        ]
        + ["star" + str(i) for i in range(1, 12)],
        "rules": [(["appointment_date", "resignation_date"], utils.get_date)],
    },
    "18-060-425_main": {
        "rows": lambda fn: utils.csv_read(fn, use_dict=False, skip=1),
        "fields": [
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
        ],
        "rules": [
            (
                ["incident_start", "incident_end", "complaint_date", "closed_date"],
                utils.parse_date,
            )
        ],
    },
    "18-060-425_accused": {
        "rows": lambda fn: utils.csv_read(fn, use_dict=False, skip=1),
        "fields": [
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
        ],
        "rules": [(["race"], utils.convert_race)],
    },
    "P0-46957_accused": {
        "rows": lambda fn: get_accused(fn),
        "fields": [
            "complaint_no",
            "name",
            "birthyear",
            "gender",
            "race",
            "appointment_date",
            "unit_no",
            "position_description",
            "star",
            "complaint_category",
            "finding",
            "discipline",
            "final_finding",
            "final_discipline",
        ],
        "id_fields": [
            "name",
            "birthyear",
            "gender",
            "race",
            "appointment_date",
            "star",
        ],
        "rules": [
            (["appointment_date"], utils.get_date),
            (["complaint_no", "birthyear", "star"], utils.to_int),
            (["race"], utils.convert_race),
        ],
    },
    "P0-46987": {
        "rows": lambda fn: utils.csv_read(fn, use_dict=False, skip=1),
        "fields": [
            "unit",
            "description",
            "active"
        ],
        "rules": [],
    },
}
