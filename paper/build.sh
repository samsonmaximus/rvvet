#!/bin/sh
# Build the methods paper. Run rvvet/scripts/analyze.py first: it writes numbers.tex, tab_*.tex
# and ../figures/*.pdf, which are copied here.
set -e
cd "$(dirname "$0")"
cp ../figures/fig_*.pdf .
cp ../forward_test/fig_timesplit.pdf .
cat part_front.tex part_abstract.tex part_methods.tex part_results.tex part_bench.tex \
    part_verify.tex part_end.tex part_apptable.tex > rvvet_methods.tex
pdflatex -interaction=nonstopmode rvvet_methods.tex > build.log 2>&1 || true
bibtex rvvet_methods > bib.log 2>&1 || true
pdflatex -interaction=nonstopmode rvvet_methods.tex > build.log 2>&1 || true
pdflatex -interaction=nonstopmode rvvet_methods.tex > build.log 2>&1 || true
grep -n "^!" rvvet_methods.log && exit 1 || true
grep -n "undefined" rvvet_methods.log || true
