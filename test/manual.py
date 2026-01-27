from startrace import *
import pytest



def run():
    """"""
    test = Trace(trace='Hello There! {num}', vars=[{'type': 'const', 'name': 'num', 'val': 42}])
    print(test)

if __name__ == '__main__':
    run()