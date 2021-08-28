RAW := raw
LOG_LEVEL := debug
SRC := src
PYTHON := LOG_LEVEL=${LOG_LEVEL} python3

.PHONY: all
all: check finalize

.PHONY: black
black:
	black .

.PHONY: check
check:
	${PYTHON} -c 'import ${SRC}'

#### Parsing ####

PARSED := tidy
PARSED_FILES := P0-46360_main.csv P0-46360_discharges.csv P0-46360_members.csv \
	P0-46360_stars.csv 16-1105.csv P4-41436.csv P0-52262.csv P0-58155.csv \
	18-060-425_main.csv 18-060-425_accused.csv P0-46957_main.csv \
	P0-46957_investigators.csv P0-46957_accused.csv P0-46987.csv \
        P0-61715.csv P5-06887.csv salary-01.csv salary-02.csv salary-03.csv
PARSED_FILES := $(addprefix ${PARSED}/, ${PARSED_FILES})

.PHONY: prepare
prepare: check ${PARSED_FILES}


${RAW}/P0-61715/Awards_Data_(New_Copy).csv: ${RAW}/P0-61715/Awards_Data_(New_Copy).zip
	${PYTHON} ${SRC}/unzip.py "$<"
	${PYTHON} ${SRC}/parse_p061715.py "$@"

.INTERMEDIATE: ${RAW}/P0-61715/Awards_Data_(New_Copy).csv

${PARSED}/P0-46957_main.csv ${PARSED}/P0-46957_investigators.csv &: ${RAW}/P0-46957 ${SRC}/parse_p046957.py
	${PYTHON} ${SRC}/parse_p046957.py $(@D) $<

${PARSED}/%.csv:
	${PYTHON} ${SRC}/parse.py "$@" "$<"

${PARSED}/P0-46957_accused.csv: ${RAW}/P0-46957
${PARSED}/P0-46360_main.csv: ${RAW}/P0-46360/10655-FOIA-P046360-TRRdata.xlsx
${PARSED}/P0-46360_members.csv: ${RAW}/P0-46360/10655-FOIA-P046360-TRRdata.xlsx
${PARSED}/P0-46360_discharges.csv: ${RAW}/P0-46360/10655-FOIA-P046360-TRRdata.xlsx
${PARSED}/P0-46360_stars.csv: ${RAW}/P0-46360/10655-FOIA-P046360-TRRdata.xlsx
${PARSED}/16-1105.csv: ${RAW}/16-1105/Kalven_16-1105_All_Sworn_Employees.xlsx
${PARSED}/P4-41436.csv: ${RAW}/P4-41436/P441436-current_and_former_CPD_employee_list_run_15_Mar_2018_by_CPD_IT-redacted_1.xlsx
${PARSED}/P0-52262.csv: ${RAW}/P0-52262/FOIA_P052262_-_11221-FOIA-P052262-AllSwornEmployeesWithUOA.xlsx
${PARSED}/P0-58155.csv: ${RAW}/P0-58155/P058155_-_Kiefer.xlsx
${PARSED}/18-060-425_main.csv: ${RAW}/18-060-425/case_info_export.xlsx
${PARSED}/18-060-425_accused.csv: ${RAW}/18-060-425/accused_export.xlsx
${PARSED}/P0-46987.csv: ${RAW}/P0-46987/units.csv
${PARSED}/P0-61715.csv: ${RAW}/P0-61715/Awards_Data_(New_Copy).csv
${PARSED}/P5-06887.csv: ${RAW}/P5-06887/P506887_Sinclair_Rajiv_Awards\ Data.xlsx
${PARSED}/salary-01.csv: ${RAW}/salary/9-13-17_FOIA_Updated_CPD_Data-2002-2007.xls
${PARSED}/salary-02.csv: ${RAW}/salary/9-13-17_FOIA_Updated_CPD_Data-2008-2012.xls
${PARSED}/salary-03.csv: ${RAW}/salary/9-13-17_FOIA_Updated_CPD_Data_-2013-2017.xls

${PARSED_FILES}: ${SRC}/parse.py | ${PARSED}

${PARSED}:
	mkdir -p $@

#### Linking ####

LINKED := final
LINKED_FILES := officer_profiles.csv unit_assignments.csv complaints_officers.csv complaints.csv tactical_response_reports.csv tactical_response_reports_discharges.csv unit_descriptions.csv awards.csv salary.csv roster.csv erroneous_officers.csv
LINKED_FILES := $(addprefix ${LINKED}/, ${LINKED_FILES})

.PHONY: finalize
finalize: check ${LINKED_FILES} clean_assignments

${LINKED}/officer_profiles.csv: ${PARSED}/P0-58155.csv ${PARSED}/P4-41436.csv ${SRC}/merge_roster.py
	${PYTHON} ${SRC}/merge_roster.py $@ $^

${LINKED}/unit_assignments.csv: ${PARSED}/16-1105.csv ${PARSED}/P0-52262.csv ${SRC}/merge_history.py | ${LINKED}/officer_profiles.csv
	${PYTHON} ${SRC}/merge_history.py $@ $^ $|

${LINKED}/complaints_officers.csv: ${PARSED}/P0-46957_accused.csv ${SRC}/link_p046957.py | ${LINKED}/unit_assignments.csv ${LINKED}/officer_profiles.csv
	${PYTHON} ${SRC}/link_p046957.py $@ $^ $|

${LINKED}/complaints.csv: ${PARSED}/P0-46957_main.csv
	cp $< $@

${LINKED}/tactical_response_reports.csv: ${PARSED}/P0-46360_main.csv ${PARSED}/P0-46360_stars.csv ${SRC}/link_p046360.py | ${LINKED}/complaints_officers.csv ${LINKED}/officer_profiles.csv 
	${PYTHON} ${SRC}/link_p046360.py $@ $^ $|

${LINKED}/tactical_response_reports_discharges.csv: ${PARSED}/P0-46360_discharges.csv
	cp $< $@

${LINKED}/erroneous_officers.csv: ${SRC}/find_erroneous.py | ${LINKED}/officer_profiles.csv ${LINKED}/unit_assignments.csv  ${LINKED}/tactical_response_reports.csv
	${PYTHON} ${SRC}/find_erroneous.py $@ $|

${LINKED}/awards.csv: ${PARSED}/P0-61715.csv ${PARSED}/P5-06887.csv ${SRC}/merge_awards.py | ${LINKED}/erroneous_officers.csv ${LINKED}/officer_profiles.csv 
	${PYTHON} ${SRC}/merge_awards.py $@ $^ $|

${LINKED}/salary.csv: ${PARSED}/salary-01.csv ${PARSED}/salary-02.csv ${PARSED}/salary-03.csv ${SRC}/merge_salary.py | ${LINKED}/awards.csv ${LINKED}/officer_profiles.csv  ${LINKED}/erroneous_officers.csv
	${PYTHON} ${SRC}/merge_salary.py $@ $^ $|

${LINKED}/roster.csv: ${LINKED}/officer_profiles.csv ${SRC}/generate_roster.py | ${LINKED}/salary.csv
	${PYTHON} ${SRC}/generate_roster.py $@ $^

${LINKED}/unit_descriptions.csv: ${PARSED}/P0-46987.csv ${PARSED}/P0-58155.csv ${PARSED}/16-1105.csv ${PARSED}/P0-46360_main.csv ${PARSED}/P0-46957_accused.csv ${PARSED}/P0-52262.csv ${SRC}/unit_descriptions.py
	${PYTHON} ${SRC}/unit_descriptions.py $@ $^

.PHONY: clean_assignments
clean_assignments: ${LINKED}/unit_assignments.csv ${LINKED}/roster.csv
	${PYTHON} ${SRC}/clean_assignments.py $^

${LINKED_FILES}: | ${LINKED}

${LINKED}:
	mkdir -p $@

.PHONY: clean
clean:
	rm -rf ${PARSED} ${LINKED}

.PHONY: documentation
documentation:
	${MAKE} -C doc

.PHONY: release
release: documentation finalize
	zip -r cpd-dataset-`git describe --tags --abbrev=0`.zip final/ doc/main.pdf CC-BY-NC-SA-LICENSE.txt MIT-LICENSE.txt description.md examples/ -x ".\*"

