#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys

# Unigrams already dropped, One sided (will be run on reversed again)
# Relaxed version can not separated by sides!
stack = []
for line in sys.stdin:
    ngram, freq, glue, stat = line.rstrip().split('\t')
    glue = float(glue)
    while stack and ngram.find(stack[-1][0] + ' ') != 0:
        sngram, sfreq, sglue, sstat = stack.pop()
        print('{}\t{}\t{:.18f}\t{}'.format(sngram, sfreq, sglue, sstat))
    if stack:  # stack[-1] is prefix of line
        if stack[-1][2] < glue:
            stack[-1][3] = '-'
        elif stack[-1][2] > glue:
            stat = '-'
    stack.append([ngram, freq, glue, stat])

sys.stdout.writelines('{}\t{}\t{:.18f}\t{}\n'.format(ngram, freq, glue, stat)
                      for ngram, freq, glue, stat in reversed(stack))
