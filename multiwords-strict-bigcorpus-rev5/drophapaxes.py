#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys

sys.stdout.writelines(line for line in sys.stdin if '1' != line.split('\t', 2)[1]) # No strip, no need to add newlines!
