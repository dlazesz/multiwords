#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys

prefixes = []
for line in sys.stdin:
    ngram, freq, *freqs = line.rstrip().split('\t', 2)
    prefixes = [(prefix, freqency) for prefix, freqency in prefixes if ngram.startswith(prefix)]
    print(ngram, freq, *freqs, '[{0}]'.format(', '.join(frequency for prefix, frequency in prefixes)), sep='\t')
    prefixes.append((ngram + ' ', freq))  # This is needed to skip equality check! And only full words is counted!
