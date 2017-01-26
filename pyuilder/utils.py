import platform
import os
import re
from functools import wraps
import inspect

def initializer(func):
    """
    Automatically assigns the parameters.

    >>> class process:
    ...     @initializer
    ...     def __init__(self, cmd, reachable=False, user='root'):
    ...         pass
    >>> p = process('halt', True)
    >>> p.cmd, p.reachable, p.user
    ('halt', True, 'root')
    """
    names, varargs, keywords, defaults = inspect.getargspec(func)

    @wraps(func)
    def wrapper(self, *args, **kargs):
        for name, arg in list(zip(names[1:], args)) + list(kargs.items()):
            setattr(self, name, arg)

        for name, default in zip(reversed(names), reversed(defaults)):
            if not hasattr(self, name):
                setattr(self, name, default)

        func(self, *args, **kargs)

    return wrapper

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def platform_specific_path(path):
    if platform.system() == 'Windows':
        return path.replace('/c/', 'C:\\').replace('/', '\\')
    else:
        return path

def get_proxy_parameters_from_env():
    proxy = os.environ.get('http_proxy')
    if proxy:
        m = re.search('http://([/.*\S.*/]+):([/.*\S.*/]+)', proxy)
        if m != None and len(m.groups()) == 2:
            return {'PROXY_HOST': m.group(1),
                    'PROXY_PORT': m.group(2),
                    'PROXY_PROTOCOL': "http",
                    'NO_PROXY': '127.0.0.1,localhost'}
    return {}

def parse_properties(file):
    without_comments = list(filter(lambda line : not line.startswith('#'), open(file)))
    return dict(line.strip().split('=') for line in without_comments)

def kwargs_to_dict(**kwargs):
    return kwargs