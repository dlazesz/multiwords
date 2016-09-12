#! /usr/bin/env python3
import sys

for line in sys.stdin:
    if '1' != line.split('\t', 2)[1]:
        sys.stdout.write(line)
