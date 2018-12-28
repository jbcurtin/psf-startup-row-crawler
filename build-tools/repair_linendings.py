#!/usr/bin/env python

import csv
import sys

filepath = sys.argv[1]
DATUMS = []

with open(filepath, 'r') as stream:
  reader = csv.reader(stream)
  DATUMS = [row for row in reader]

with open(filepath, 'w') as stream:
  writer = csv.writer(stream)
  for row in DATUMS:
    writer.writerow(row)

print(filepath)
print('Awe')

