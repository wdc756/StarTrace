# This file was used because I don't know how pytest works and how to get debug lines out

from startrace.star_trace import *

x = 10
y = lambda x: x * 2
test_context = {
    "x": x,
    "y": y
}
z = 20
test_link_context = {
    "z": z
}
t_dict = {
    "tokens": [
        {"type": "link", "link": "y(x)", "context": {}},
        {"type": "const", "value": " "},
        {"type": "link", "link": "y(z)", "context": test_link_context}
    ],
    "global_context": test_context,
    "eval_allowed": True
}
pat = Pattern(t_dict)
assert len(pat) == 3
print(pat.evaluate())
assert pat.evaluate() == "20 40"
