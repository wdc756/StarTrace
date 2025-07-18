# This file was used because I don't know how pytest works and how to get debug lines out

from startrace.star_trace import *

import numpy as np

values = np.arange(0, 10, 1)
tok = Token('test', values)
assert tok.phrases[0] == 'test'
assert tok.num == 0
assert tok.iter.start == 0
assert tok.iter.end == 9
assert tok.iter.step == 1

