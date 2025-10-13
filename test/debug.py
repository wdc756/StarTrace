# This file was used because I don't know how pytest works and how to get debug lines out

from startrace.star_trace import *

z = []
links = {"z": z}
tok = LinkToken("z[0]", links, True, False)
z.append(2)
assert tok.evaluate() == "2"
