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

    def prefix_object_name(self, prefix):
        """Adds a prefix to the object name."""

        self.object_name = prefix + self.object_name

    __str__ = lambda self: self.get_message()

    if _PY2:
        __unicode__ = __str__
        __str__ = lambda self: self.get_message().encode()


class InvalidTypeError(ValidationError):
    """Invalid object type (according to schema)."""

    def __init__(self, obj, name=""):
        super(InvalidTypeError, self).__init__(
            name, "Invalid object type.")
        self.object_type = type(obj)

    def get_message(self):
        return "{0} has an invalid type: {1}.".format(
            self.object_name, self.object_type.__name__)


class InvalidValueError(ValidationError):
    """Invalid object value (according to schema)."""

    def __init__(self, value, name=""):
        super(InvalidValueError, self).__init__(
            name, "Invalid object value.")
        self.object_value = value

    def get_message(self):
        return "{0} has an invalid value: {1}.".format(
            self.object_name, _repr(self.object_value))


class UnknownParameterError(ValidationError):
    """Unknown object's key (according to schema)."""

    def __init__(self, name):
        super(UnknownParameterError, self).__init__(
            name, "Unknown parameter.")

    def get_message(self):
        return "Unknown parameter: {0}.".format(self.object_name)


class MissingParameterError(ValidationError):
    """A required object's key is missing. (according to schema)"""

    def __init__(self, name):
        super(MissingParameterError, self).__init__(
            name, "Parameter is missing.")

    def get_message(self):
        return "{0} is missing.".format(self.object_name)



class Object(object):
    """Base class for all validators."""

    optional = False
    """True if the object value is optional."""


    def __init__(self, optional=False):
        if optional:
            self.optional = True


    def validate(self, obj):
        """Validates the specified object.

        Returns the validated object (possibly modified to satisfy the schema
        or a new valid converted object - it's depends on validator) or raises
        an exception inherited from ValidationError.
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


    def validate(self, obj):
        """Validates the specified object."""

        if type(obj) not in self._types:
            raise InvalidTypeError(obj)

        if self.__choices is not None and obj not in self.__choices:
            raise InvalidValueError(obj)

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
    """List validator."""

    __scheme = None
    """Value scheme."""

    def __init__(self, scheme=None, **kwargs):
        super(List, self).__init__(**kwargs)

        if scheme is not None:
            self.__scheme = scheme


    def validate(self, obj):
        """Validates the specified object."""

        if type(obj) is not list:
            raise InvalidTypeError(obj)

        if self.__scheme is not None:
            for index, value in enumerate(obj):
                try:
                    obj[index] = validate_scheme(value, self.__scheme)
                except ValidationError as e:
                    e.prefix_object_name("[{0}]".format(index))
                    raise

        return obj



class Dict(Object):
    """Dictionary validator."""

    __key_scheme = None
    """Key scheme."""

    __value_scheme = None
    """Value scheme."""


    def __init__(self, key_type=None, value_type=None, **kwargs):
        super(Dict, self).__init__(**kwargs)

        if key_type is not None:
            self.__key_scheme = key_type

        if value_type is not None:
            self.__value_scheme = value_type


    def validate(self, obj):
        if type(obj) is not dict:
            raise InvalidTypeError(obj)

        for key, value in obj.items():
            try:
                if self.__key_scheme is None:
                    valid_key = key
                else:
                    # TODO: name
                    valid_key = validate_scheme(key, self.__key_scheme)

                if self.__value_scheme is None:
                    valid_value = value
                else:
                    valid_value = validate_scheme(value, self.__value_scheme)

                if valid_key is not key:
                    del obj[key]
                    obj[valid_key] = valid_value
                elif valid_value is not value:
                    obj[valid_key] = valid_value
            except ValidationError as e:
                e.prefix_object_name(_dict_key_name(key))
                raise

        return obj



class DictScheme(Object):
    __ignore_unknown = False

    def __init__(self, scheme, ignore_unknown=False, **kwargs):
        super(DictScheme, self).__init__(**kwargs)
        self.__scheme = scheme
        if ignore_unknown:
            self.__ignore_unknown = True


    def validate(self, obj):
        if type(obj) is not dict:
            raise InvalidTypeError(obj)

        if not self.__ignore_unknown:
            unknown = set(obj) - set(self.__scheme)
            if unknown:
                raise UnknownParameterError(_dict_key_name(unknown.pop()))

        for key, scheme in self.__scheme.items():
            if key not in obj:
                if scheme.optional:
                    # TODO: iterate over scheme?
                    continue
                else:
                    raise MissingParameterError(_dict_key_name(key))

            try:
                obj[key] = validate_scheme(obj[key], scheme)
            except ValidationError as e:
                e.prefix_object_name(_dict_key_name(key))
                raise

        return obj


def validate_scheme(obj, scheme):
    return scheme.validate(obj)

def validate_object(name, obj, scheme):
    try:
        return validate_scheme(obj, scheme)
    except ValidationError as e:
        e.prefix_object_name(name)
        raise

def _list_value_name(list_name, index):
    return "{0}[{1}]".format(list_name, index)

def _dict_key_name(key):
    return "[{0}]".format(_repr(key))

if _PY2:
    def _repr(value):
        return repr(value)[1:] if type(value) is str else repr(value)
else:
    _repr = repr
