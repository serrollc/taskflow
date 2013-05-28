# -*- coding: utf-8 -*-

# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright (C) 2012 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import collections
import functools
import inspect

# These arguments are ones that we will skip when parsing for requirements
# for a function to operate (when used as a task).
AUTO_ARGS = ('self', 'context',)


def _take_arg(a):
    if a in AUTO_ARGS:
        return False
    # In certain decorator cases it seems like we get the function to be
    # decorated as an argument, we don't want to take that as a real argument.
    if isinstance(a, collections.Callable):
        return False
    return True


def wraps(fn):
    """This will not be needed in python 3.2 or greater which already has this
    built-in to its functools.wraps method."""

    def wrapper(f):
        f = functools.wraps(fn)(f)
        f.__wrapped__ = getattr(fn, '__wrapped__', fn)
        return f

    return wrapper


def requires(*args, **kwargs):

    def decorator(f):
        if not hasattr(f, 'requires'):
            f.requires = set()

        if kwargs.pop('auto_extract', True):
            inspect_what = f
            if hasattr(f, '__wrapped__'):
                inspect_what = f.__wrapped__
            f_args = inspect.getargspec(inspect_what).args
            f.requires.update([a for a in f_args if _take_arg(a)])

        f.requires.update([a for a in args if _take_arg(a)])

        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    # This is needed to handle when the decorator has args or the decorator
    # doesn't have args, python is rather weird here...
    if kwargs or not args:
        return decorator
    else:
        if isinstance(args[0], collections.Callable):
            return decorator(args[0])
        else:
            return decorator


def provides(*args, **kwargs):

    def decorator(f):
        if not hasattr(f, 'provides'):
            f.provides = set()

        f.provides.update([a for a in args if _take_arg(a)])

        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    # This is needed to handle when the decorator has args or the decorator
    # doesn't have args, python is rather weird here...
    if kwargs or not args:
        return decorator
    else:
        if isinstance(args[0], collections.Callable):
            return decorator(args[0])
        else:
            return decorator
