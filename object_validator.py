"""Validates an object against a schema."""

from __future__ import unicode_literals

import re
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

    def get_message(self):
        """Returns the error message."""

        return getattr(super(ValidationError, self), "__unicode__" if _PY2 else "__str__")()

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


class InvalidListLength(ValidationError):
    """Invalid list length (according to schema)."""

    def __init__(self, value, name=""):
        super(InvalidListLength, self).__init__(
            name, "Invalid list length.")
        self.object_value = value

    def get_message(self):
        return "{0} has an invalid length: {1}.".format(
            self.object_name, len(self.object_value))


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


class ParameterAlreadyExistsError(ValidationError):
    """
    A parameter name has been converted to a value that already exists in the
    object.
    """

    def __init__(self, name=""):
        super(ParameterAlreadyExistsError, self).__init__(
            name, "Parameter already exists.")

    def get_message(self):
        return "{0} already exists.".format(self.object_name)


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


class _BasicNumber(_BasicType):
    """Base class for number type validators."""

    __min = None
    """Minimum value."""

    __max = None
    """Maximum value."""

    def __init__(self, min=None, max=None, **kwargs):
        if min is not None:
            self.__min = min

        if max is not None:
            self.__max = max

        super(_BasicNumber, self).__init__(**kwargs)

    def validate(self, obj):
        """Validates the specified object."""

        obj = super(_BasicNumber, self).validate(obj)

        if (
            self.__min is not None and obj < self.__min or
            self.__max is not None and obj > self.__max
        ):
            raise InvalidValueError(obj)

        return obj


class Bool(_BasicType):
    """Boolean type validator."""
    _types = (bool,)


class Float(_BasicNumber):
    """Float type validator."""
    _types = (float,)


class Integer(_BasicNumber):
    """Integer type validator."""

    _types = (int, long) if _PY2 else (int,)


class String(_BasicType):
    """String type validator."""

    _types = (str,)

    __min_length = None
    """Minimum length."""

    __max_length = None
    """Maximum length."""

    __regex = None
    """Regular expression the string must match to."""

    def __init__(self, min_length=None, max_length=None, regex=None, **kwargs):
        if min_length is not None:
            self.__min_length = min_length

        if max_length is not None:
            self.__max_length = max_length

        if regex is not None:
            if isinstance(regex, (str, bytes)):
                regex = re.compile(regex)
            self.__regex = regex

        super(String, self).__init__(**kwargs)

    def validate(self, obj):
        """Validates the specified object."""

        obj = super(String, self).validate(obj)

        if (
            self.__min_length is not None and len(obj) < self.__min_length or
            self.__max_length is not None and len(obj) > self.__max_length or
            self.__regex is not None and self.__regex.search(obj) is None
        ):
            raise InvalidValueError(obj)

        return obj


class List(Object):
    """List validator."""

    __scheme = None
    """Value scheme."""

    __min_length = None
    """Minimum length."""

    __max_length = None
    """Maximum length."""

    def __init__(self, scheme=None, min_length=None, max_length=None, **kwargs):
        super(List, self).__init__(**kwargs)

        if scheme is not None:
            self.__scheme = scheme

        if min_length is not None:
            self.__min_length = min_length

        if max_length is not None:
            self.__max_length = max_length

    def validate(self, obj):
        """Validates the specified object."""

        if type(obj) is not list:
            raise InvalidTypeError(obj)

        if (
            self.__min_length is not None and len(obj) < self.__min_length or
            self.__max_length is not None and len(obj) > self.__max_length
        ):
            raise InvalidListLength(obj)

        if self.__scheme is not None:
            for index, value in enumerate(obj):
                try:
                    obj[index] = validate_object(value, self.__scheme)
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

    def __init__(self, key_scheme=None, value_scheme=None, **kwargs):
        super(Dict, self).__init__(**kwargs)

        if key_scheme is not None:
            self.__key_scheme = key_scheme

        if value_scheme is not None:
            self.__value_scheme = value_scheme

    def validate(self, obj):
        """Validates the specified object."""

        if type(obj) is not dict:
            raise InvalidTypeError(obj)

        for key, value in tuple(obj.items()):
            try:
                valid_key = key if self.__key_scheme is None \
                    else validate_object(key, self.__key_scheme)

                valid_value = value if self.__value_scheme is None \
                    else validate_object(value, self.__value_scheme)
            except ValidationError as e:
                e.prefix_object_name(_dict_key_name(key))
                raise

            if valid_key is not key:
                del obj[key]

                if valid_key in obj:
                    raise ParameterAlreadyExistsError(_dict_key_name(valid_key))

                obj[valid_key] = valid_value
            elif valid_value is not value:
                obj[valid_key] = valid_value

        return obj


class DictScheme(Object):
    """Validator for a dictionary against a dictionary key scheme."""

    __ignore_unknown = False
    """Ignore unknown keys."""

    __delete_unknown = False
    """Delete unknown keys."""

    def __init__(self, scheme, ignore_unknown=False, delete_unknown=False, **kwargs):
        super(DictScheme, self).__init__(**kwargs)

        self.__scheme = scheme

        if ignore_unknown:
            self.__ignore_unknown = True

        if delete_unknown:
            self.__delete_unknown = True

    def validate(self, obj):
        """Validates the specified object."""

        if type(obj) is not dict:
            raise InvalidTypeError(obj)

        if self.__delete_unknown:
            for key in set(obj) - set(self.__scheme):
                del obj[key]
        elif not self.__ignore_unknown:
            unknown = set(obj) - set(self.__scheme)
            if unknown:
                raise UnknownParameterError(_dict_key_name(unknown.pop()))

        for key, scheme in self.__scheme.items():
            if key in obj:
                try:
                    obj[key] = validate_object(obj[key], scheme)
                except ValidationError as e:
                    e.prefix_object_name(_dict_key_name(key))
                    raise
            else:
                if _get_optional(scheme) is None:
                    raise MissingParameterError(_dict_key_name(key))

        return obj


def validate(name, obj, scheme):
    """Validates the specified object."""

    try:
        return validate_object(obj, scheme)
    except ValidationError as e:
        e.prefix_object_name(name)
        raise


def validate_object(obj, scheme):
    """Validates the specified object.

    Note: this function is for internal usage only (from validators). It's
    needed for possible support for example a list of schemes as a scheme in
    the future.
    """

    return scheme.validate(obj)


def _get_optional(scheme):
    """Returns the scheme if it's optional or None otherwise.

    Note: this function is for internal usage only (from validators). It's
    needed for possible support for example a list of schemes as a scheme in
    the future.
    """

    return scheme if scheme.optional else None


def _dict_key_name(key):
    """Formats a key to object name suffix."""

    return "[{0}]".format(_repr(key))


_repr = (lambda obj: repr(obj)[1:] if type(obj) is str else repr(obj)) if _PY2 else repr
"""More friendly version of repr()."""
