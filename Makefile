RAW := raw
LOG_LEVEL := debug
SRC := src
PYTHON := LOG_LEVEL=${LOG_LEVEL} python3

.PHONY: all
all: link

.PHONY: black
black:
	black .

.PHONY: check
check:
	${PYTHON} -c 'import ${SRC}'

#### Parsing ####

PARSED := parsed
PARSED_FILES := P0-46360_main.csv P0-46360_discharges.csv P0-46360_members.csv \
	P0-46360_stars.csv 16-1105.csv P4-41436.csv P0-52262.csv P0-58155.csv \
	18-060-425_main.csv 18-060-425_accused.csv P0-46957_main.csv \
	P0-46957_investigators.csv P0-46957_accused.csv P0-46987.csv \
        P0-61715.csv P5-06887.csv
PARSED_FILES := $(addprefix ${PARSED}/, ${PARSED_FILES})

.PHONY: parse
parse: check ${PARSED_FILES}

${PARSED}/P0-46957_main.csv ${PARSED}/P0-46957_investigators.csv &: ${RAW}/P0-46957 | ${PARSED}
	${PYTHON} ${SRC}/parse_p046957.py $(@D) $<

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
${PARSED}/P0-61715.csv: ${RAW}/P0-61715/Awards_Data_(New_Copy).zip
${PARSED}/P5-06887.csv: ${RAW}/P5-06887/P506887_Sinclair_Rajiv_Awards\ Data.xlsx

${PARSED}/%.csv: | ${PARSED}
	${PYTHON} ${SRC}/parse.py "$@" "$<"

${PARSED}:
	mkdir -p $@

#### Linking ####

LINKED := linked
LINKED_FILES := profiles.csv history.csv P0-46957_accused.csv P0-46957_main.csv P0-46360_main.csv roster.csv
LINKED_FILES := $(addprefix ${LINKED}/, ${LINKED_FILES})

.PHONY: link
link: ${LINKED_FILES}

${LINKED}/profiles.csv: ${PARSED}/P0-58155.csv ${PARSED}/P4-41436.csv | ${LINKED}
	${PYTHON} ${SRC}/merge_roster.py $^ $@

${LINKED}/history.csv: ${PARSED}/16-1105.csv ${PARSED}/P0-52262.csv ${LINKED}/profiles.csv | ${LINKED}
	${PYTHON} ${SRC}/merge_history.py $^ $@

${LINKED}/P0-46957_accused.csv: ${PARSED}/P0-46957_accused.csv ${LINKED}/profiles.csv | ${LINKED}
	${PYTHON} ${SRC}/link_p046957.py $^ $@

${LINKED}/P0-46957_main.csv: ${PARSED}/P0-46957_main.csv | ${LINKED}
	cp $< $@

${LINKED}/P0-46360_main.csv: ${PARSED}/P0-46360_main.csv ${PARSED}/P0-46360_stars.csv ${LINKED}/profiles.csv | ${LINKED}
	${PYTHON} ${SRC}/link_p046360.py $^ $@

${LINKED}/P0-46360_discharges.csv: ${PARSED}/P0-46360_discharges.csv | ${LINKED}
	cp $< $@

${LINKED}/roster.csv: ${LINKED}/profiles.csv | ${LINKED}
	${PYTHON} ${SRC}/clean_profiles.py $^ $@

${LINKED}:
	mkdir -p $@

.PHONY: clean
clean:
	rm -rf ${PARSED} ${LINKED}
