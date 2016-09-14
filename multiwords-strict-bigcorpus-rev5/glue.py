#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys


# Refer to the paper to learn about this function
def _dice(freq, pref_freqencies, suf_freqencies):
    pref_freqencies = list(pref_freqencies)
    suf_freqencies = list(suf_freqencies)
    # 2 * freq / sum (average(pref), average(suf))
    return 2 * freq / (sum(pref_freqencies)/len(pref_freqencies) + sum(suf_freqencies)/len(suf_freqencies))


# Refer to the paper to learn about this function
def _scp(freq, pref_freqencies, suf_freqencies):
    multiplied = [lfreq * rfreq for lfreq, rfreq in zip(pref_freqencies, suf_freqencies)]
    # freq^2 / sum(avg(multiplied)) = (freq^2 * len(multiplied)) / sum(multiplied) (Latter is more stable numerically)
    return (freq ** 2 * len(multiplied)) / sum(multiplied)

gfuns = {'dice': _dice, 'scp': _scp}
if 2 != len(sys.argv) or sys.argv[1] not in gfuns:
    sys.exit('usage: {} (dice|scp)'.format(sys.argv[0]))
gfun = gfuns[sys.argv[1]]

for line in sys.stdin:
    line = line.rstrip()  # we will use it to compose the output
    _, inp_freq, pref_freqs, suf_freqs = line.split('\t')
    glue = gfun(int(inp_freq),
                map(int, pref_freqs[1:-1].split(', ')),
                map(int, reversed(suf_freqs[1:-1].split(', '))))
    print(line, '{:0.18f}'.format(glue), sep='\t')  # Fixed output format for comparing!
