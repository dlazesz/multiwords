#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys

for line in sys.stdin:
    ngram, *freqs = line.rstrip().split('\t')
    print(' '.join(reversed(ngram.split())), *freqs, sep='\t')
