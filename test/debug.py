# This file was used because I don't know how pytest works and how to get debug lines out

from startrace.star_trace import *

tok = RangeToken(3, 1, -1)
assert tok.iter.value == 3
assert tok.next() == True
assert tok.last() == True
assert tok.last() == False
