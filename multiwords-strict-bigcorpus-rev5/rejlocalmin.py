#! /usr/bin/env python3
import collections
import sys

class Line():
    __slots__ = 'n', 'ngram', 'freq', 'glue', 'stat'
    def __init__(self, line):
        ngram, self.freq, glue, self.stat = line.rstrip().split('\t')
        self.ngram = ngram.split()
        self.n = len(self.ngram)
        self.glue = float(glue)

    def __str__(self):
        f = '{}\t{}\t{}\t{}'.format
        return f(' '.join(self.ngram), self.freq, self.glue, self.stat)

    def isprefixof(self, other):
        return self.n < other.n and other.ngram[:self.n] == self.ngram

stack = []
for line in map(Line, sys.stdin):
    while stack and not stack[-1].isprefixof(line):
        print(stack.pop())
    if stack: # stack[-1] is prefix of line
        assert(stack[-1].n == line.n - 1)
        if stack[-1].glue < line.glue:
            stack[-1].stat = '-'
        elif stack[-1].glue > line.glue:
            line.stat = '-'
    stack.append(line)

while stack:
    print(stack.pop())
