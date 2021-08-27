# `roster.csv`, `officer_profiles.csv`, and `erroneous_officers.csv`

In `officer_profiles.csv`:
- `last_name`, `first_name`, `middle_initial`: fields containing the officer's name
- `gender`: officer gender (CPD's categorization is binary: `M` or `F`)
- `race`: officer race (CPD's categorization: `WHITE`, `BLACK`, `WHITE HISPANIC`, `BLACK HISPANIC`, `ASIAN/PACIFIC ISLANDER`, `AMER IND/ALASKAN NATIVE`, `UNKNOWN`)
- `birthyear`: officer birthyear
- `age`: officer age (as of when?)
- `status`: ?
- `appointment_date`: date in the format `YYYY-MM-DD` (of what?)
- `position_no`: an internal numerical code representing position. E.g. `9161` is `POLICE OFFICER`, `9111` is `CROSSING GUARD`
- `position_description`: a human-readable position name
- `unit_no`: the officer's assigned unit (as of when?)
- `unit_description`: a human-readable unit description
- `resignation_date`: the date of the officer's resignation in the format `YYYY-MM-DD`, or empty if they have not resigned
- `star,star1,star2,star3,star4,star5,star6,star7,star8,star9,star10,star11`: fields for officer badge numbers
- `sworn`: whether this is a sworn officer (`Y` or `N`)
- `unit_id`: an internal unit identification number (should this be here?)
- `unit_detail`: ??
- `source`: the FOIA release in which this profile was found (`salary` is the only release for which the FOIA number is unknown, so this is just labeled `salary`)
- `uid`: the unique ID for the officer to which this profile pertains

`roster.csv` is just a "flattening" of `officer_profiles.csv` to have exactly one row per UID. For each collection of profiles having one UID, `roster.csv` fills each field using the most recent non-missing entry among the profiles. In other words, each row in `roster.csv` corresponds to a single individual, and each column is the most recent available information for that individual and field. 

`erroneous_officers.csv` is just a plain list of UIDs that are likely to correspond to erroneous database entries.

# `unit_assignments.csv` and `unit_descriptions.csv`

In `unit_assignments.csv`:
- `uid`: the unique ID for the officer to which the record pertains
- `unit_no`: the CPD unit number (names are available in `unit_descriptions.csv`)
- `start_date` and `end_date`: the start and end date for the assignment

In `unit_descriptions.csv`:
- `unit_no`: contains the CPD unit number
- `unit_description`: the name of the unit from CPD records. These names were collected from both the unit reference table provided in `P0-46987` and throughout the remainder of the data, where available. There *are* other units with duplicated numbers that existed in the original unit reference table, but these have been removed when they do not appear in the remainder of the data (e.g. officer unit assignments).
- `active_status`: whether the unit was active as of the `status_date` 
- `status_date`: the date for the `active_status`


# `complaints.csv` and `complaints_officers.csv`

In `complaints.csv`:
- complaint_no
- beat
- location_code
- street_no
- street_name
- apt_no
- city
- incident_datetime
- complaint_date
- closed_date

In `complaints_officers.csv`:
- complaint_no
- complaint_category
- finding
- discipline
- final_finding
- final_discipline
- uid

# `tactical_response_reports.csv` and `tactical_response_reports_discharges.csv`

In `tactical_response_reports.csv`:
- trr_id
- rd_no
- cr_no_obtained
- subject_cb_no
- event_no
- beat
- block
- street_direction
- street_name
- location
- date
- time
- indoor_or_outdoor
- lighting_condition
- weather_condition
- notify_oemc
- notify_dist_sergeant
- notify_op_command
- notify_det_div
- number_of_weapons_discharged
- party_fired_first
- duty_status
- injured
- member_in_uniform
- subject_gender
- subject_race
- subject_age
- subject_birthyear
- subject_armed
- subject_injured
- subject_alleged_injury
- uid

In `tactical_response_reports_discharges.csv`:
- trr_id
- weapon_type
- weapon_type_descr
- firearm_make
- firearm_model
- firearm_barrel_length
- firearm_caliber
- total_number_of_shots
- firearm_reloaded
- number_of_catdridge_reloaded
- handgun_worn_type
- handgun_drawn_type
- method_used_to_reload
- sight_used
- protective_cover_used
- discharge_distance
- object_struck_of_discharge
- discharge_position

# `awards.csv`
- `uid`:
- `star`:
- `position_no`:
- `position_description`:
- `award_request_date`:
- `award_ref_number`:
- `award_type`:
- `requester_last_name`:
- `requester_first_name`:
- `requester_middle_initial`:
- `tracking_no`:
- `current_status`:
- `incident_start_date`:
- `incident_end_date`:
- `incident_description`:
- `ceremony_date`:

# `salary.csv`
- `uid`:
- `year`:
- `salary`:
- `position_description`:
- `pay_grade`:
- `present_posn_start_date`:
- `officer_date`:
- `employee_status`:


