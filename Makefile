PYTHON := python3
RAW := raw
CLEAN := cleaned
OUTPUT := P0-46360_main.csv P0-46360_discharges.csv P0-46360_members.csv \
	P0-46360_stars.csv 16-1105.csv P4-41436.csv P0-52262.csv P0-58155.csv \
	18-060-425_main.csv 18-060-425_accused.csv P0-46957_main.csv \
	P0-46957_investigators.csv P0-46957_accused.csv
OUTPUT := $(addprefix ${CLEAN}/, ${OUTPUT})

.PHONY: all
all: ${OUTPUT}

.INTERMEDIATE: ${RAW}/18-060-425/case_info_export.csv ${RAW}/18-060-425/accused_export.csv
${RAW}/18-060-425/%.csv: ${RAW}/18-060-425/%.xlsx
	xlsx2csv -n "Export Worksheet" $< $@

${CLEAN}/P0-46957_main.csv ${CLEAN}/P0-46957_investigators.csv &: ${RAW}/P0-46957 | ${CLEAN}
	${PYTHON} p046957.py $@ $<

${CLEAN}/P0-46957_accused.csv: ${RAW}/P0-46957
${CLEAN}/P0-46360_main.csv: ${RAW}/P0-46360/10655-FOIA-P046360-TRRdata.xlsx
${CLEAN}/P0-46360_members.csv: ${RAW}/P0-46360/10655-FOIA-P046360-TRRdata.xlsx
${CLEAN}/P0-46360_discharges.csv: ${RAW}/P0-46360/10655-FOIA-P046360-TRRdata.xlsx
${CLEAN}/P0-46360_stars.csv: ${RAW}/P0-46360/10655-FOIA-P046360-TRRdata.xlsx
${CLEAN}/16-1105.csv: ${RAW}/16-1105/Kalven_16-1105_All_Sworn_Employees.xlsx
${CLEAN}/P4-41436.csv: ${RAW}/P4-41436/P441436-current_and_former_CPD_employee_list_run_15_Mar_2018_by_CPD_IT-redacted_1.xlsx
${CLEAN}/P0-52262.csv: ${RAW}/P0-52262/FOIA_P052262_-_11221-FOIA-P052262-AllSwornEmployeesWithUOA.xlsx
${CLEAN}/P0-58155.csv: ${RAW}/P0-58155/P058155_-_Kiefer.xlsx
${CLEAN}/18-060-425_main.csv: ${RAW}/18-060-425/case_info_export.csv
${CLEAN}/18-060-425_accused.csv: ${RAW}/18-060-425/accused_export.csv

${CLEAN}/%.csv: | ${CLEAN}
	${PYTHON} clean.py $@ $<

${CLEAN}:
	mkdir -p $@

.PHONY: clean
clean:
	rm -rf ${CLEAN}
