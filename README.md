<p align="center">
<img src="https://upload.wikimedia.org/wikipedia/commons/e/e0/Chicago_%282551781706%29.jpg" width="600" class="center"/>
<h1 align="center">The CPD Data Set</h1>
</p>

This repository contains data related to the activities of ~35,000 police officers
in the Chicago Police department (CPD), including ~11,000 tactical response reports
from 2004-2016 and ~110,000 civilian and administrative complaints from 2000-2018.
The data was obtained following a series of
requests covered by the Freedom of Information Act (FOIA) and coordinated by
the [Invisible Institute](https://invisible.institute/).

Details about the FOIA requests and which information about the CPD they cover
can be found in the file [`raw/datasets.csv`](raw/datasets.csv). The original
data which serves as a starting point for this repository was imported from the
Invisible Institute's [download page](https://invisible.institute/download-the-data)

# Requirements

### Code
This code requires **Python>=3.8** and GNU Make 4.3 (it will not work on earlier versions).
You will require [xlrd](https://github.com/python-excel/xlrd) and
[openpyxl](https://openpyxl.readthedocs.io/en/stable/) to read `.xls` and `.xlsx` files,
respectively. Optionally, if you are planning to contribute changes to the code in this
repository, you will need the [black](https://github.com/psf/black) package for code formatting.

All Python dependencies can be installed by running

```console
pip install -r requirements.txt
```
in the repository root folder.

### Documentation (optional)

We have included a `.pdf` of the documentation in the current release version.
But if you want to compile the documentation yourself from the source file `docs/main.tex`, you can 
either compile it however you normally would with your favourite LaTeX compiler 
(e.g. with `pdflatex` and `bibtex`), or you can run
```console
make
```
in the `docs/` folder to compile it with [latexrun](https://github.com/aclements/latexrun). 


# Obtaining the data

In order to build the cleaned and linked data, run
```console
make
```
in the repository root folder. This will result in the creation of a single cleaned and linked
set of data in the `final/` folder, where all records (officers, complaints, and tactical response reports) are associated
with unique IDs that enable linkage among the records. 

### How the data are processed

See the documentation `main.pdf` for an in-depth discussion of the data cleaning and linking.
In brief, the `make` command will result in two primary data processing steps.
First, in the **cleaning** step, the raw Excel files are converted to `.csv` files and field
names are uniformized across files. To perform *just* the cleaning step, run the following command
in the repository root folder:
```console
make prepare
```
This will create a `tidy/` folder containing cleaned versions of the original raw data.

Second, in the **linking** step, records of officers
appearing in the different data files are linked by cleaning and matching their attributes,
removing erroneous entries, etc. The linking step produces the final clean data files
listed above. To perform *just* the linking step (after you have already run the cleaning
step), the following command in the repository root folder:
```console
make finalize
```
This will create a `final/` folder containing the final cleaned and linked version of the data.


# Data description

Once you have completed the above build step, the repository will contain
the cleaned and linked data. In particular, the following files will have been generated:
- `final/roster.csv`: A merged and linked roster of all unique officers in the data
- `final/officer_profiles.csv`: A list of all officers, including duplicate entries when an officer appears in multiple source files
- `final/erroneous_officers.csv`: A list of probable erroneous/duplicate officer records in the original data
- `final/unit_assignments.csv`: A list of unit assignments for each officer with start and end date
- `final/unit_descriptions.csv`: A list of unit names
- `final/complaints.csv`: Formal complaints filed against officers
- `final/complaints_officers.csv`: The officers involved in the complaints, with allegations, findings, and sanctions
- `final/tactical_response_reports.csv`: Forms that officers are required to file when their response involves use of force
- `final/tactical_response_reports_discharges.csv`: ??
- `final/awards.csv`: A list of awards requested for officers, request date, and result
- `final/salary.csv`: A list of officer salaries, positions, and paygrades

### `roster.csv`, `officer_profiles.csv`, and `erroneous_officers.csv`

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

### `tactical_response_reports.csv` and `tactical_response_reports_discharges.csv`

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

# License

The code that cleans and links the data, as well as the code that produces the
documentation for this project, is licensed under the [MIT License](https://opensource.org/licenses/MIT);
see `MIT-LICENSE.txt` for the license text.
The dataset that is produced by the code is licensed under the 
[Creative Commons 4.0 Attribution NonCommercial ShareAlike License](https://creativecommons.org/licenses/by-nc-sa/4.0/);
see `CC-BY-NC-SA-LICENSE.txt` for the license text.

The header image in this README is by [Bert Kaufmann via Wikimedia Commons (CC BY 2.0)](https://commons.wikimedia.org/wiki/File:Chicago_(2551781706).jpg).




