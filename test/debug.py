# This file was used because I don't know how pytest works and how to get debug lines out

from startrace.star_trace import *
import numpy as np



t_dict = [
    {"type": "c_str", "value": "test"},
    {"type": "c_str", "value": "0"},
    {"type": "r_val", "start": 1, "end": 3, "step": 1},
    {"type": "d_val", "values": [1, 2, 3]},
    {"type": "d_str", "values": ["token", "dict"]}
]
pat = Pattern(t_dict)
assert pat.tokens[0].phrases[0] == 'test'
assert pat.tokens[1].phrases[0] == '0'
assert pat.tokens[1].num is None
assert pat.tokens[2].phrases[0] == ''
assert pat.tokens[2].iter.start == 1
assert pat.tokens[2].iter.end == 3
assert pat.tokens[2].iter.step == 1
assert pat.tokens[3].phrases == ['1', '2', '3']
assert pat.tokens[3].num == 0
assert pat.tokens[4].phrases == ['token', 'dict']