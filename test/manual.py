from startrace import *
from typing import Any
import pytest



def run():
    """"""
    def get_project_name(currentError: Link) -> str:
        return currentError.val
    def get_device_name(currentDevice: Link) -> str:
        return currentDevice.val
    def get_error(currentError: Link) -> Any:
        return currentError.val
    currentProject = Link(val='Project Name')
    currentDevice = Link(val='Device Name')
    currentError = Link(val='Error')
    links = {
        'name': {
            'val': get_project_name,
            'args': [currentProject],
        },
        'device_name': {
            'val': get_device_name,
            'args': [currentDevice],
        },
        'error': {
            'val': get_error,
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
    }
    trace_dict['links'] = links
    trace = Trace(**trace_dict)

    print(trace)
    currentProject.val = 'Test'
    currentDevice.val = 42
    currentError.val = 1
    print(trace)


if __name__ == '__main__':
    run()