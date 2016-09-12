#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys

if 2 != len(sys.argv):
    sys.exit('usage: {} MAXN'.format(sys.argv[0]))

maxn = int(sys.argv[1])
for line in sys.stdin:
    grams = line.rstrip().split()
    if grams:
        sys.stdout.writelines('{0}\n'.format(' '.join(grams[i:i + n])) for n in range(1, min(maxn + 1, len(grams) + 1))
                              for i in range(len(grams) - n + 1))
