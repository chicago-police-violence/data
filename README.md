<img src="https://cdn.theatlantic.com/thumbor/9jB6mGx0eREfH3l82uNckcwrUFI=/0x62:2343x1380/1952x1098/media/img/mt/2018/03/AP_429077000333/original.jpg" width="700" class="center"/>

# The CPD35K Data

This repository contains data related to the activities of roughly 35,000 police officers 
in the Chicago Police department (CPD) as
well as code to process it. The data was obtained following a series of
requests covered by the Freedom of Information Act (FOIA) and coordinated by
the Invisible Institute.

Details about the FOIA requests and which information about the CPD they cover
can be found in the file `datasets.csv`.

# Requirements

You will require [xlrd](https://github.com/python-excel/xlrd) and
[openpyxl](https://openpyxl.readthedocs.io/en/stable/) to read `.xls` and
`.xlsx` files, respectively. Optionally, if you are planning to make changes
to this repository, you will need the [black](https://github.com/psf/black)
package for code formatting.

All dependencies can be installed by running

```
pip install -r requirements.txt
```
in the repository root folder.

# Obtaining the data

The data in this repository exists in its raw format, as obtained in multiple FOIA requests.
These files may be found in the `raw` folder, with one subfolder per FOIA request.
Each subfolder contains the original Excel data files along
with the request and answer letters when available.

In order to build the cleaned and linked data, run
```
make
```
in the repository root folder. This will result in the creation of a single cleaned and linked
set of data where all records (officers, complaints, and tactical response reports) are associated
with unique IDs that enable linkage among the records. In particular, the following files are generated:
- `linked/roster.csv`: A merged and linked roster of all unique officers in the data
- `linked/profiles.csv`: A roster of all officers, including duplicate entries when an officer appears in multiple source files
- `linked/history.csv`: A history of unit membership of each officer
- `linked/P0-46360_main.csv`: (TBD)
- `linked/P0-46957_accused.csv`: (TBD)
- `linked/P0-46957_main.csv`: (TBD)

### `roster.csv`

Fill in details

### `profiles.csv`

### `history.csv`

### `P0-46360_main.csv`

### `P0-46957_accused.csv`

### `P0-46957_main.csv`

# Parsing and Linking

In more detail, the `make` command will result in two primary data processing steps.
First, in the **parsing** step, the raw Excel files are converted to `.csv` files and field
names are uniformized across files. Then in the **linking** step, 

## Parsing

In the first stage, the raw Excel files are parsed and converted to `.csv`
files for easier later processing. This stage can be ran with

```
make parse
```

which will create and populate the `parsed` folder.


Virtually no decision is made at this stage regarding cleaning or interpreting
the data beyond uniformizing field names across datasets. Hence, even if you
are not willing to use or trust the output of the later processing stages,
there is probably no reason not to use the output of this stage as opposed to
working directly with the original data.

## Linking

```
make link
```
