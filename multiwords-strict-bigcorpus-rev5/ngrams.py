#! /usr/bin/env python3
import sys

if 2 != len(sys.argv):
    sys.exit('usage: {} MAXN'.format(sys.argv[0]))

maxn = int(sys.argv[1])
for line in sys.stdin:
    grams = line.rstrip().split()
    if not grams: continue
    for n in range(1, maxn + 1):
        if n > len(grams): break
        for i in range(len(grams) - n + 1):
            print(*grams[i:i + n])
