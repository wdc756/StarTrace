from startrace import *
from typing import Any
import pytest



def run():
    """"""
    currentProject = Link(val='Project Name')
    currentDevice = Link(val='Device Name')
    currentError = Link(val='Error')
    links = {
        'name': {
            'val': lambda project: project.val,
            'args': [currentProject],
        },
        'device_name': {
            'val': lambda device: device.val,
            'args': [currentDevice],
        },
        'error': {
            'val': lambda error: error.val,
            'args': [currentError],
        }
    }

    trace_dict = {
        'trace': '{name}: {device_name}: {error}',
        'vars': [
            {'type': 'link', 'name': 'name'},
            {'type': 'link', 'name': 'device_name'},
            {'type': 'link', 'name': 'error'},
        ],
        'links': links,
    }
    trace = Trace(**trace_dict)

    print(trace)
    currentProject.val = 'Test'
    currentDevice.val = 42
    currentError.val = 1
    print(trace)


if __name__ == '__main__':
    run()