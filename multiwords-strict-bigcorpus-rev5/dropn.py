#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys

# No strip, no need to add newlines!
n = int(sys.argv[1])
sys.stdout.writelines(line for line in sys.stdin if n != len(line.split('\t', 1)[0].split()))
