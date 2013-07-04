"""Validates a JSON against a schema."""

from __future__ import unicode_literals

import sys

_PY2 = sys.version_info < (3,)
if _PY2:
    str = unicode


class Error(Exception):
    """Base class for all exceptions the module throws."""

    def __init__(self, error, *args, **kwargs):
        super(Error, self).__init__(
            error.format(*args, **kwargs) if args or kwargs else error)


class ValidationError(Error):
    """Base class for all validation errors."""

    def __init__(self, name, *args, **kwargs):
        super(ValidationError, self).__init__(*args, **kwargs)
        self.object_name = name


class InvalidTypeError(ValidationError):
    """Invalid object type (according to schema)."""

    def __init__(self, name, obj):
        self.object_type = type(obj)
        super(InvalidTypeError, self).__init__(
            name, "{0} has an invalid type: {1}.",
            name, self.object_type.__name__)


class InvalidValueError(ValidationError):
    """Invalid object value (according to schema)."""

    def __init__(self, name, value):
        super(InvalidValueError, self).__init__(
            name, "{0} has an invalid value: {1!r}.", name, value)
        self.object_value = value


class UnknownParameterError(ValidationError):
    """Unknown object's key (according to schema)."""

    def __init__(self, name):
        super(UnknownParameterError, self).__init__(
            name, "Unknown parameter: {0}.", name)


class MissingParameterError(ValidationError):
    """A required object's key is missing. (according to schema)"""

    def __init__(self, name):
        super(MissingParameterError, self).__init__(
            name, "{0} is missing.", name)



class Object(object):
    """Base class for all validators."""

    optional = False
    """True if the object value is optional."""


    def __init__(self, optional=False):
        if optional:
            self.optional = True


    def validate(self, name, obj):
        """Validates the specified object.

        Returns the validated object (or a valid converted value of the
        object) or raises an exception inherited from ValidationError.
        """

        raise Error("Not implemented.")



class _BasicType(Object):
    """Base class for basic type validators."""

    __choices = None
    """A list of values we must to compare the validated object with."""


    def __init__(self, choices=None, **kwargs):
        super(_BasicType, self).__init__(**kwargs)

        if choices is not None:
            self.__choices = choices


    def validate(self, name, obj):
        """Validates the specified object."""

        if type(obj) not in self._types:
            raise InvalidTypeError(name, obj)

        if self.__choices is not None and obj not in self.__choices:
            raise InvalidValueError(name, obj)

        return obj



class Bool(_BasicType):
    """Boolean type validator."""
    _types = (bool,)


class Float(_BasicType):
    """Float type validator."""
    _types = (float,)


class Integer(_BasicType):
    """Integer type validator."""
    _types = (int, long) if _PY2 else (int,)


class String(_BasicType):
    """String type validator."""
    _types = (str,)



class List(Object):
    def __init__(self, template, **kwargs):
        super(List, self).__init__(**kwargs)
        self.__type = template


    def validate(self, name, obj):
        if type(obj) is not list:
            raise InvalidTypeError(name, obj)

        for index, value in enumerate(obj):
            obj[index] = self.__type.validate(
                _list_value_name(name, index), value)

        return obj



class AbstractDict(Object):
    __key_type = None
    __value_type = None

    def __init__(self, key_type=None, value_type=None, **kwargs):
        super(AbstractDict, self).__init__(**kwargs)

        if key_type is not None:
            self.__key_type = key_type

        if value_type is not None:
            self.__value_type = value_type


    def validate(self, name, obj):
        if type(obj) is not dict:
            raise InvalidTypeError(name, obj)

        for key, value in obj.items():
            if self.__key_type is None:
                valid_key = key
            else:
                # TODO: name
                valid_key = validate(_dict_key_name(name, key),
                    key, self.__key_type)

            if self.__value_type is None:
                valid_value = value
            else:
                valid_value = validate(_dict_key_name(name, key),
                    value, self.__value_type)

            if valid_key is not key:
                del obj[key]
                obj[valid_key] = valid_value
            elif valid_value is not value:
                obj[valid_key] = valid_value

        return obj


class Dict(Object):
    __ignore_unknown = False

    def __init__(self, template, ignore_unknown=False, **kwargs):
        super(Dict, self).__init__(**kwargs)
        self.__template = template
        if ignore_unknown:
            self.__ignore_unknown = True


    def validate(self, name, obj):
        if type(obj) is not dict:
            raise InvalidTypeError(name, obj)

        if not self.__ignore_unknown:
            unknown = set(obj) - set(self.__template)
            if unknown:
                raise UnknownParameterError(_dict_key_name(name, unknown.pop()))

        for key, template in self.__template.items():
            key_name = _dict_key_name(name, key)

            if key not in obj:
                if template.optional:
                    # TODO: iterate over template?
                    continue
                else:
                    raise MissingParameterError(key_name)

            obj[key] = template.validate(key_name, obj[key])

        return obj


def validate(name, obj, template):
    return template.validate(name, obj)

def _list_value_name(list_name, index):
    return "{0}[{1}]".format(list_name, index)

def _dict_key_name(dict_name, key_name):
    return "{0}[{1!r}]".format(dict_name, key_name)
