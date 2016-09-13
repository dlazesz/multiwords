#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import json
import sys


def _avg(ls):
    return sum(ls) / len(ls)


# Refer to the paper to learn about this function
def _dice(freq, split_freqs):
    return 2 * freq / sum(map(_avg, zip(*split_freqs)))


# Refer to the paper to learn about this function
def _scp(freq, split_freqs):
    return freq ** 2 / _avg([lfreq * rfreq for lfreq, rfreq in split_freqs])


gfuns = {'dice': _dice, 'scp': _scp}
if 2 != len(sys.argv) or sys.argv[1] not in gfuns:
    sys.exit('usage: {} (dice|scp)'.format(sys.argv[0]))
gfun = gfuns[sys.argv[1]]

for line in sys.stdin:
    line = line.rstrip()  # we will use it to compose the output
    ngram, inp_freq, pref_freqs, suf_freqs = line.split('\t')
    pref_freqs, suf_freqs = json.loads(pref_freqs), json.loads(suf_freqs)
    glue = gfun(int(inp_freq), zip(pref_freqs, reversed(suf_freqs)))
    print(line, glue, sep='\t')