#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys
import json

prefixes = []
for line in sys.stdin:
    ngram, *freqs = line.rstrip().split('\t')
    prefixes = [(pref, freq) for pref, freq in prefixes if ngram.startswith(pref)]
    freqs.append(json.dumps([freq for pref, freq in prefixes]))
    print(ngram, *freqs, sep='\t')
    prefixes.append((ngram + ' ', int(freqs[0])))
