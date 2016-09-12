#! /usr/bin/env python3
import sys

for line in sys.stdin:
    ngram, *freqs = line.rstrip().split('\t')
    print(' '.join(reversed(ngram.split())), *freqs, sep='\t')
