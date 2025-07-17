# This file was used because I don't know how pytest works and how to get debug lines out

from startrace.star_trace import *



tok = Token(['test', 'token'])
assert tok.phrases[0] == 'test'
assert tok.phrases[1] == 'token'
assert tok.num == 0
assert tok.iter.start == 0
assert tok.iter.end == 1
assert tok.iter.step == 1
