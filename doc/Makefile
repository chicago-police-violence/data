.PHONY: all clean FORCE

all: main.pdf

%.pdf: FORCE
	latexrun -W all -W no-xcolor $*.tex

clean:
	latexrun --clean-all
	rm -rf latex.out

watch:
	watchman-make -p '**/*.tex' '*.bib' -t all
