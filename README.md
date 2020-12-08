# Overview

This repository contains data related to the Chicago Police department (CPD) as
well as code to process it. The data was obtained following a series of
requests covered by the Freedom of Information Act (FOIA) and coordinated by
the Invisible Institute.

Details about the FOIA requests and which information about the CPD they cover
can be found in the file `datasets.csv`.

# Requirements

[xlrd](https://github.com/python-excel/xlrd) and
[openpyxl](https://openpyxl.readthedocs.io/en/stable/) to read `.xls` and
`.xlsx` files respectively. Optionally, [black](https://github.com/psf/black)
if planning to make changes to this repository. Dependencies can be installed
with

```
pip install -r requirements.txt
```

# Organization and processing

Raw datasets are contained in the `raw` folder with one subfolder per FOIA
request. Each subfolder contains the (Excel) files as originally received along
with the request and answer letters when available.

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

## Merging and linking

```
make link
```
