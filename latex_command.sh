#!/bin/bash
cd Tex
rm -f main.pdf
mkdir -p output
mkdir -p output/tasks
pdflatex -output-directory=output main.tex
mv output/main.pdf ../
cd ..