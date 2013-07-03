from __future__ import unicode_literals

# TODO: slots?

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


class UnknownParameter(ValidationError):
    def __init__(self, name):
        super(UnknownParameter, self).__init__(
            name, "Unknown parameter: {0}.", name)


class MissingParameter(ValidationError):
    def __init__(self, name):
        super(MissingParameter, self).__init__(
            name, "{0} is missing.", name)



class Object(object):
    def validate(self, obj, name):
        raise Exception("Not implemented.")



class _BasicType(Object):
    def validate(self, obj, name):
        if type(obj) not in self._types:
            raise ValidationError(name, "{0} has an invalid type ({1}).",
                name, type(obj).__name__)


class Bool(_BasicType):
    _types = (bool,)

class Float(_BasicType):
    _types = (float,)

class Integer(_BasicType):
    if _PY2:
        _types = (int, long)
    else:
        _types = (int,)

class String(_BasicType):
    _types = (str,)


class Dict(Object):
    __ignore_unknown = False

    def __init__(self, template, ignore_unknown=False, **kwargs):
        super(Dict, self).__init__(**kwargs)
        self.__template = template
        if ignore_unknown:
            self.__ignore_unknown = True


    def validate(self, obj, name):
        if type(obj) is not dict:
            raise ValidationError(name, "{0} has an invalid type ({1}).",
                name, type(obj).__name__)

        if not self.__ignore_unknown:
            unknown = set(obj) - set(self.__template)
            if unknown:
                raise UnknownParameter(_dict_key_name(name, unknown.pop()))

        for key, template in self.__template.items():
            key_name = _dict_key_name(name, key)

            if key not in obj:
                raise MissingParameter(key_name)

            template.validate(obj[key], key_name)


def _dict_key_name(dict_name, key_name):
    return "{0}[{1!r}]".format(dict_name, key_name)
