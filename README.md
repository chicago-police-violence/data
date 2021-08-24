<p align="center">
<img src="https://cdn.theatlantic.com/thumbor/9jB6mGx0eREfH3l82uNckcwrUFI=/0x62:2343x1380/1952x1098/media/img/mt/2018/03/AP_429077000333/original.jpg" width="700" class="center"/>
</p>

# The CPD Data Set

This repository contains data related to the activities of ~35,000 police officers
in the Chicago Police department (CPD), including ~11,000 tactical response reports
from 2004-2016 and ~110,000 civilian and administrative complaints from 2000-2018.
The data was obtained following a series of
requests covered by the Freedom of Information Act (FOIA) and coordinated by
the [Invisible Institute](https://invisible.institute/).

Details about the FOIA requests and which information about the CPD they cover
can be found in the file [`src/datasets.csv`](src/datasets.csv). The original
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

We have included a `.pdf` of the documentation in `docs/main.pdf`.
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
- `linked/roster.csv`: A merged and linked roster of all unique officers in the data
- `linked/profiles.csv`: A roster of all officers, including duplicate entries when an officer appears in multiple source files
- `linked/history.csv`: A history of unit membership of each officer
- `linked/P0-46360_main.csv`: (TBD)
- `linked/P0-46957_accused.csv`: (TBD)
- `linked/P0-46957_main.csv`: (TBD)

### `roster.csv`

Fill in details for each of these: field names and their meanings

### `profiles.csv`

### `history.csv`

### `P0-46360_main.csv`

### `P0-46957_accused.csv`

### `P0-46957_main.csv`

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



