from startrace import *
import pytest



def run():
    """"""
    dct = {
        'trace': 'const={const}, range={range}, list={list}, time={time}',
        'vars': [
            {'type': 'const', 'name': 'const', 'val': 'Hello There!'},
            {'type': 'range', 'name': 'range', 'iter': {'start': 1, 'end': 3, 'step': 1}},
            {'type': 'list', 'name': 'list', 'vals': [3, 5, 4]},
            {'type': 'time', 'name': 'time', 'mode': 'datetime'},
        ]
    }
    test = Trace(**dct)
    for trace in test:
        print(trace)

if __name__ == '__main__':
    run()