from __future__ import unicode_literals

import sys

_PY2 = sys.version_info < (3,)
if _PY2:
    str = unicode

class Error(Exception):
    """The base class for all exceptions that the module raises."""

    def __init__(self, error, *args, **kwargs):
        super(Error, self).__init__(error.format(*args, **kwargs) if args or kwargs else error)


class ValidationError(Error):
    """Error during validation."""

    def __init__(self, name, *args, **kwargs):
        super(ValidationError, self).__init__(*args, **kwargs)


class Object(object):
    def validate(self, obj, name):
        raise Exception("Not implemented.")



class String(Object):
    def validate(self, obj, name):
        if type(obj) is not str:
            raise ValidationError(name, "{0} has an invalid type ({1}).",
                name, type(obj).__name__)


class Dict(Object):
    def validate(self, obj, name):
        if type(obj) is not dict:
            raise ValidationError(name, "{0} has an invalid type ({1}).",
                name, type(obj).__name__)
