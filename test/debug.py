# This file was used because I don't know how pytest works and how to get debug lines out

from startrace.star_trace import *
import numpy as np


pat = Pattern([
        ConstToken("test"),
        ListToken([1, 2, 3]),
        RangeToken(1, 3, 1)
    ])

while True:
    print(pat.evaluate())
    if not pat.next():
        break

print()
print(pat.evaluate())
pat.next()
print(pat.evaluate())
pat.last()
print(pat.evaluate())
pat.next()
print(pat.evaluate())