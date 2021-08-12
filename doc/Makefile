PAPER = subliminal
TEX = $(wildcard *.tex)
BIB = refs.bib

.PHONY: all clean FORCE

all: main.pdf

%.pdf: FORCE
	latexrun -W all -W no-xcolor $*.tex

clean:
	latexrun --clean-all
	rm -rf latex.out notes.tar.gz

build:
	git archive -o notes.tar.gz master

watch:
	watchman-make -p '**/*.tex' '*.bib' -t all
