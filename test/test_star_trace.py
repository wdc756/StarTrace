# This file contains a few tests to run before pushing a new version

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from StarTrace.star_trace import *



def test_parameters():
    tok = Token(TokenType.PHRASE, 'test')
    assert tok.type == TokenType.PHRASE
    assert tok.phrase[0] == 'test'
    assert tok.num == 0
    assert tok.iter.start == 0
    assert tok.iter.end == 0
    assert tok.iter.step == 1

    tok = Token(TokenType.INCR, 'token', 1.0, Iter(0.0, 1.0, 1.0))
    assert tok.type == TokenType.INCR
    assert tok.phrase[0] == 'token'
    assert tok.num == 1.0
    assert tok.iter.start == 0.0
    assert tok.iter.end == 1.0
    assert tok.iter.step == 1.0

    tok = Token(TokenType.PHRASE, ['test', 'token'])
    assert tok.type == TokenType.PHRASE
    assert tok.phrase[0] == 'test'
    assert tok.phrase[1] == 'token'
    assert tok.num == 0
    assert tok.iter.start == 0
    assert tok.iter.end == 1
    assert tok.iter.step == 1



    pat = Pattern([
        Token(TokenType.PHRASE, 'test'),
        Token(TokenType.INCR, 'token', 0.0, Iter(0.0, 0.0, 1.0))
    ])
    assert pat.tokens[0].type == TokenType.PHRASE
    assert pat.tokens[0].phrase[0] == 'test'
    assert pat.tokens[0].num == 0
    assert pat.tokens[1].type == TokenType.INCR
    assert pat.tokens[1].phrase[0] == 'token'
    assert pat.tokens[1].num == 0.0

def test_alternate_inputs():
    # tok = Token(0, '')
    # assert tok.type == TokenType.PHRASE

    tok = Token(TokenType.PHRASE, '', 0, (0, 0, 1))
    assert tok.iter.start == 0.0
    assert tok.iter.end == 0.0
    assert tok.iter.step == 1.0



    pat = Pattern([
        Token(TokenType.PHRASE, 'test'),
        tok
    ])
    assert pat.tokens[0].type == TokenType.PHRASE
    assert pat.tokens[0].phrase[0] == 'test'
    assert pat.tokens[1].type == TokenType.PHRASE
    assert pat.tokens[1].phrase[0] == ''
    assert pat.tokens[1].num == 0.0
    assert pat.tokens[1].iter.start == 0.0
    assert pat.tokens[1].iter.end == 0.0
    assert pat.tokens[1].iter.step == 1.0

def test_invalid_inputs():
    with pytest.raises(TypeError):
        Token(TokenType.PHRASE, 'test', 0.0)

    with pytest.raises(TypeError):
        Token(TokenType.INCR, 'token', 0, Iter(0.0, 1.0, 1.0))

    with pytest.raises(ValueError):
        Token(TokenType.INCR, '', 0, Iter(1, 0, 1))

    with pytest.raises(ValueError):
        Token(TokenType.PHRASE, ['test', 'token'], 0, Iter(0, 2, 1))

    with pytest.raises(ValueError):
        Token(TokenType.PHRASE, ['test', 'token'], 2, Iter(0, 1, 1))

    with pytest.raises(TypeError):
        Iter(0, 1, 1.0)

def test_pattern():
    pat = Pattern([
        Token(TokenType.PHRASE, 'test_'),
        Token(TokenType.INCR, 'token:', 0, Iter(0, 0, 1))
    ])
    assert pat.get_pattern() == 'test_token:0'

    pat = Pattern([
        Token(TokenType.PHRASE, ['testing_', 'test_']),
        Token(TokenType.INCR, 'token:', 1, Iter(0, 1, 1)),
    ])
    assert pat.get_pattern() == 'testing_token:1'

def test_increment():
    pat = Pattern([
        Token(TokenType.PHRASE, 'test_'),
        Token(TokenType.INCR, 'token:', 0, Iter(0, 5, 1))
    ])
    for i in range(5):
        assert pat.get_pattern() == 'test_token:' + str(i)
        pat.increment()

    pat = Pattern([
        Token(TokenType.PHRASE, ['testing_', 'test_']),
        Token(TokenType.PHRASE, 'token')
    ])
    assert pat.get_pattern() == 'testing_token'
    pat.increment()
    assert pat.get_pattern() == 'test_token'
    pat.increment()
    assert pat.get_pattern() == 'testing_token'

    pat = Pattern([
        Token(TokenType.PHRASE, 'test_'),
        Token(TokenType.INCR, '', 0, Iter(0, 2, 1)),
        Token(TokenType.INCR, '', 0, Iter(0, 9, 1))
    ])
    for i in range(3):
        assert pat.get_pattern() == 'test_' + str(i) + '0'
        for j in range(10):
            assert pat.get_pattern() == 'test_' + str(i) + str(j)
            pat.increment()

if __name__ == '__main__':
    test_parameters()