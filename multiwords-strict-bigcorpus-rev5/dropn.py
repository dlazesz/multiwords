#! /usr/bin/env python3
import sys

n = int(sys.argv[1])
for line in sys.stdin:
    if n != len(line.split('\t', 1)[0].split()):
        sys.stdout.write(line)
