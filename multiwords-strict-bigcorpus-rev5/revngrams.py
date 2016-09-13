#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys

# Analogous: mawk -F'\t' -v OFS='\t' '{n=split($1, ngram, " "); $1=""; for (i=n; i>1; i--) printf("%s ",ngram[i]); printf("%s%s%s", ngram[1], $0, ORS) }'
for line in sys.stdin:
    ngram, freqs = line.rstrip().split('\t', 1)
    print(' '.join(reversed(ngram.split())), freqs, sep='\t')
