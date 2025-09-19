#!/bin/bash
cd Tex
mkdir -p output
mkdir -p output/tasks
pdflatex -output-directory=output main.tex
mv output/main.pdf ../
rm -r output
cd ..