### `roster.csv`, `officer_profiles.csv`, and `erroneous_officers.csv`

In `officer_profiles.csv`:
- `last_name`, `first_name`, `middle_initial`: fields containing the officer's name
- `gender`: officer gender (CPD's categorization is binary: `M` or `F`)
- `race`: officer race (CPD's categorization: `WHITE`, `BLACK`, `WHITE HISPANIC`, `BLACK HISPANIC`, `ASIAN/PACIFIC ISLANDER`, `AMER IND/ALASKAN NATIVE`, `UNKNOWN`)
- `birthyear`: officer birthyear
- `age`: officer age at the time the CPD answered the FOIA request identified by source
- `status`:
- `appointment_date`: date of appointment of the officer (`YYYY-MM-DD`)
- `position_no`: an internal numerical code representing position (e.g. `9161` for `POLICE OFFICER`, `9111` for `CROSSING GUARD`)
- `position_description`: a human-readable position name
- `unit_no`: the officer's assigned unit at the time the CPD answered the FOIA request identified by `source`
- `unit_description`: a human-readable description of the unit identified by `unit_no`
- `resignation_date`: the date of the officer's resignation in the format `YYYY-MM-DD`, or empty if they have not resigned
- `star,star1,star2,star3,star4,star5,star6,star7,star8,star9,star10,star11`: fields for officer badge numbers
- `sworn`: whether this is a sworn officer (`Y` or `N`)
- `unit_id`: an internal unit identification number
- `unit_detail`:
- `source`: the FOIA release in which this profile was found (`salary` is the only release for which the FOIA number is unknown, so this is just labeled `salary`)
- `uid`: the unique ID for the officer to which this profile pertains

`roster.csv` is just a "flattening" of `officer_profiles.csv` to have exactly one row per UID. For each collection of profiles having one UID, `roster.csv` fills each field using the most recent non-missing entry among the profiles. In other words, each row in `roster.csv` corresponds to a single individual, and each column is the most recent available information for that individual and field. 

`erroneous_officers.csv` is just a plain list of UIDs that are likely to correspond to erroneous database entries.

### `unit_assignments.csv` and `unit_descriptions.csv`

In `unit_assignments.csv`:
- `uid`: the unique ID for the officer to which the record pertains
- `unit_no`: the CPD unit number (names are available in `unit_descriptions.csv`)
- `start_date` and `end_date`: the start and end date for the assignment

In `unit_descriptions.csv`:
- `unit_no`: contains the CPD unit number
- `unit_description`: the name of the unit from CPD records. These names were collected from both the unit reference table provided in `P0-46987` and throughout the remainder of the data, where available. There *are* other units with duplicated numbers that existed in the original unit reference table, but these have been removed when they do not appear in the remainder of the data (e.g. officer unit assignments).
- `active_status`: whether the unit was active as of the `status_date` 
- `status_date`: the date for the `active_status`


### `complaints.csv` and `complaints_officers.csv`

In `complaints.csv`:
- `complaint_no`: number identifying the complaint
- `beat`: beat number
- `location_code`: see https://github.com/invinst/chicago-police-data/blob/master/data/context_data/Location%20Codes.png
- `street_no`, `street_name`, `apt_no`: house number, street name and apartment number where the incident occurred
- `city`: `CHICAGO IL` occasionally followed by the zipcode where the incident occurred
- `incident_datetime`: date and time when the incident occurred (`YYYY-MM-DD HH:MM:SS`)
- `complaint_date`: date when the complaint was filed (`YYYY-MM-DD`)
- `closed_date`: date when the complaint was closed (`YYYY-MM-DD`)

In `complaints_officers.csv`:
- `complaint_no`: number identifying the complaints
- `complaint_category`: category describing the reason for the complaint (e.g. `03D-ILLEGAL ARREST`), see http://directives.chicagopolice.org/forms/CPD-44.248.pdf
- `finding`:
- `discipline`: see https://raw.githubusercontent.com/invinst/chicago-police-data/master/data/context_data/sustained_penalty_codes/sustained_penalty_codes.pdf
- `final_finding`
- `final_discipline`
- `uid`: unique ID of the officer to which the record pertains

### `tactical_response_reports.csv` and `tactical_response_reports_discharges.csv`

In `tactical_response_reports.csv`:
- `trr_id`: number identifying an (event, officer, subject) triplet
- `rd_no`:
- `cr_no_obtained`: 
- `subject_cb_no`
- `event_no`: number identifying the event
- `beat`: beat number
- `block`: partial number identifying a block (e.g. `39XX`)
- `street_direction`: cardinal direction of the street (`West`, `North`, `South` or `East`)
- `street_name`: name of the street
- `location`: type of location of the event (e.g. `SIDEWALK`, `APPARTMENT`)
- `date`: date of the event (`YYYY-MM-DD`)
- `time`: time of the event (`HH:MM:SS`)
- `indoor_or_outdoor`: whether the event occurred `Indoor` or `Outdoor`
- `lighting_condition`: lighting condition during the event (`DAYLIGHT`, `NIGHT`, `DAWN`, `DUSK`, `GOOD ARTIFICIAL` or `POOR ARTIFICIAL`)
- `weather_condition`: (e.g. `CLEAR`, `RAIN`)
- `notify_oemc`:
- `notify_dist_sergeant`:
- `notify_op_command`:
- `notify_det_div`:
- `number_of_weapons_discharged`: number of weapons discharged by the officer during the event
- `party_fired_first`: party who fired first (`MEMBER`, `OFFENDER` or `OTHER`)
- `duty_status`: whether or not the officer was on duty during the event (`Yes` or `No`)
- `injured`: whether or not the officer was injured (`Yes` or `No`)
- `member_in_uniform`: whether or not the officer was in uniform during the event
- `subject_gender`: gender of the subject (CPD's categorization `MALE` or `FEMALE`)
- `subject_race`: race of the subject (CPD's categorization as in `officer_profiles.csv`)
- `subject_age`:
- `subject_birthyear`: birth year of the subject
- `subject_armed`: whether or not the subject was armed (`Yes` or `No`)
- `subject_injured`: whether or not the subject was injured (`Yes` or `No`)
- `subject_alleged_injury`: whether or not the subject alleged to be injured (`Yes` or `No`)
- `uid`: unique ID of the officer who submitted the report

In `tactical_response_reports_discharges.csv`:
- `trr_id`:
- `weapon_type`
- `weapon_type_descr`
- `firearm_make`
- `firearm_model`
- `firearm_barrel_length`
- `firearm_caliber`
- `total_number_of_shots`
- `firearm_reloaded`
- `number_of_catdridge_reloaded`
- `handgun_worn_type`
- `handgun_drawn_type`
- `method_used_to_reload`
- `sight_used`
- `protective_cover_used`
- `discharge_distance`
- `object_struck_of_discharge`
- `discharge_position`:

### `awards.csv`
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

### `salary.csv`
- `uid`:
- `year`:
- `salary`:
- `position_description`:
- `pay_grade`:
- `present_posn_start_date`:
- `officer_date`:
- `employee_status`:


