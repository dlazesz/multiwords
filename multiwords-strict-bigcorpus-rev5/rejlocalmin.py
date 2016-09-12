#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys


class Line:
    __slots__ = 'n', 'ngram', 'freq', 'glue', 'stat'

    def __init__(self, inp_line):
        ngram, self.freq, glue, self.stat = inp_line.rstrip().split('\t')
        self.ngram = ngram.split()
        self.n = len(self.ngram)
        self.glue = float(glue)

    def __str__(self):
        return '{}\t{}\t{}\t{}'.format(' '.join(self.ngram), self.freq, self.glue, self.stat)

    def isprefixof(self, other):
        return self.n < other.n and other.ngram[:self.n] == self.ngram

stack = []
for line in map(Line, sys.stdin):
    while stack and not stack[-1].isprefixof(line):
        print(stack.pop())
    if stack:  # stack[-1] is prefix of line
        assert(stack[-1].n == line.n - 1)
        if stack[-1].glue < line.glue:
            stack[-1].stat = '-'
        elif stack[-1].glue > line.glue:
            line.stat = '-'
    stack.append(line)

sys.stdout.writelines('{0}\n'.format(s) for s in reversed(stack))
