# This file was used because I don't know how pytest works and how to get debug lines out

from StarTrace.star_trace import *



pat = Pattern([
    Token(TokenType.PHRASE, 'test_'),
    Token(TokenType.INCR, '', 0, Iter(0, 2, 1)),
    Token(TokenType.INCR, '', 0, Iter(0, 9, 1))
])
for i in range(3):
    assert pat.get_pattern() == 'test_' + str(i) + '0'
    for j in range(10):
        print(i, j)
        print(pat.get_pattern())
        assert pat.get_pattern() == 'test_' + str(i) + str(j)
        pat.increment()
    print('\n')
    print(pat.get_pattern())
    print('test_' + str(i) + '0')
