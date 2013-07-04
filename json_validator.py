from __future__ import unicode_literals

# TODO: slots?
# TODO: check return value

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


class InvalidType(ValidationError):
    def __init__(self, name, type):
        super(InvalidType, self).__init__(
            name, "{0} has an invalid type ({1}).", name, type.__name__)
        self.object_name = name


class InvalidValue(ValidationError):
    def __init__(self, name, value):
        super(InvalidValue, self).__init__(
            name, "{0} has an invalid value: {1}.", name, value)
        self.object_name = name
        self.object_value = value


class UnknownParameter(ValidationError):
    def __init__(self, name):
        super(UnknownParameter, self).__init__(
            name, "Unknown parameter: {0}.", name)
        self.object_name = name


class MissingParameter(ValidationError):
    def __init__(self, name):
        super(MissingParameter, self).__init__(
            name, "{0} is missing.", name)
        self.object_name = name



class Object(object):
    optional = False

    def __init__(self, optional=False):
        if optional:
            self.optional = True

    def validate(self, name, obj):
        raise Exception("Not implemented.")



class _BasicType(Object):
    __choices = None

    def __init__(self, choices=None, **kwargs):
        super(_BasicType, self).__init__(**kwargs)
        if choices is not None:
            self.__choices = choices

    def validate(self, name, obj):
        if type(obj) not in self._types:
            raise InvalidType(name, type(obj))

        if self.__choices is not None and obj not in self.__choices:
            raise InvalidValue(name, obj)

        return obj


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


class List(Object):
    def __init__(self, template, **kwargs):
        super(List, self).__init__(**kwargs)
        self.__type = template


    def validate(self, name, obj):
        if type(obj) is not list:
            raise InvalidType(name, type(obj))

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
            raise InvalidType(name, type(obj))

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
            raise InvalidType(name, type(obj))

        if not self.__ignore_unknown:
            unknown = set(obj) - set(self.__template)
            if unknown:
                raise UnknownParameter(_dict_key_name(name, unknown.pop()))

        for key, template in self.__template.items():
            key_name = _dict_key_name(name, key)

            if key not in obj:
                if template.optional:
                    # TODO: iterate over template?
                    continue
                else:
                    raise MissingParameter(key_name)

            obj[key] = template.validate(key_name, obj[key])

        return obj


def validate(name, obj, template):
    template.validate(name, obj)

def _list_value_name(list_name, index):
    return "{0}[{1}]".format(list_name, index)

def _dict_key_name(dict_name, key_name):
    return "{0}[{1!r}]".format(dict_name, key_name)
