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
set of data where all records (officers, complaints, and tactical response reports) are associated
with unique IDs that enable linkage among the records. 


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
- `final/awards.csv`: A list of awards requested for officers, request date, and result
- `final/salary.csv`: A list of officer salaries, positions, and paygrades

**TODO: fill in details for each of these: field names, their meanings, and any additional useful info to know about them**


### `roster.csv`, `officer_profiles.csv`, and `erroneous_officers.csv`

### `unit_assignments.csv` and `unit_descriptions.csv`

In `unit_assignments.csv`:
- `uid` is the unique ID for the officer to which the record pertains
- `unit_no` is the CPD unit number (names are available in `unit_descriptions.csv`)
- `start_date` and `end_date`: the start and end date for the assignment

In `unit_descriptions.csv`:
- `unit_no`: contains the CPD unit number
- `unit_description`: the name of the unit from CPD records. These names were collected from both the unit reference table provided in `P0-46987` and throughout the remainder of the data, where available. There *are* other units with duplicated numbers that existed in the original unit reference table, but these have been removed when they do not appear in the remainder of the data (e.g. officer unit assignments).
- `active_status`: whether the unit was active as of the `status_date` 
- `status_date`: the date for the `active_status`


### `complaints.csv` and `complaints_officers.csv`

### `tactical_response_reports.csv`

### `awards.csv`

### `salary.csv`

# How the data are processed

In more detail, the `make` command will result in two primary data processing steps.
First, in the **parsing** step, the raw Excel files are converted to `.csv` files and field
names are uniformized across files. Then in the **linking** step, records of officers
appearing in the different data files are linked by cleaning and matching their attributes,
removing erroneous entries, etc. The linking step produces the final clean data files
listed above.

## Parsing

In the first stage, the raw Excel files are parsed and converted to `.csv`
files for easier later processing. This stage can be run individually by running

```console
make prepare
```

in the repository root folder. This will create and populate the `parsed` folder.

*todo: discuss the code and its structure here*

Virtually no decision is made at this stage regarding cleaning or interpreting
the data beyond uniformizing field names across datasets. Hence, even if you
are not willing to use or trust the output of the later processing stages,
there is probably no reason not to use the output of this stage as opposed to
working directly with the original data.

## Linking

```console
make finalize
```

*todo: discuss the code and its structure here*

# License

The code that cleans and links the data, as well as the code that produces the
documentation for this project, is licensed under the [MIT License](https://opensource.org/licenses/MIT);
see `MIT-LICENSE.txt` for the license text.
The dataset that is produced by the code is licensed under the 
[Creative Commons 4.0 Attribution NonCommercial ShareAlike License](https://creativecommons.org/licenses/by-nc-sa/4.0/);
see `CC-BY-NC-SA-LICENSE.txt` for the license text.

The header image in this README is by [Bert Kaufmann via Wikimedia Commons (CC BY 2.0)](https://commons.wikimedia.org/wiki/File:Chicago_(2551781706).jpg).




