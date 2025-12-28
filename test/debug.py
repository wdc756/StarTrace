from startrace import *

test = Iter(start=0, end=3, step=1)
lisB = ListBinding(values=["H", "e", "l", "l", "o"])

for i in test:
    print(i)

print()

for i in lisB:
    print(i)


pat = Pattern(template="hello{val}", bindings=[lisB])