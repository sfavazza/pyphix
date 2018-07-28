"""Collection of utilities."""

__author__ = "Samuele FAVAZZA"
__copyright__ = "Copyright 2018, Samuele FAVAZZA"

import re


def check_kwargs(kwargs, arg_name, exp_type, default_value):
    """Check the legality of an input key-argument pair and raise ValueError if wrong.

    :param kwargs: keyword-argument dictionary.
    :param arg_name: string containing the name of the argument to check.
    :param exp_type: type or list of types accepted for the checked argument.
    :param default_value: return this value if the *arg_name* is not found in kwargs (it's type is not checked).

    :type kwargs: dict
    :type arg_name: str
    :type exp_type: any or list[any]
    :type default_value: any

    :return: *kwargs[arg_name]* if type is valid, *default_value* if *arg_name* is not in the *kwargs.keys()*.
    :rtype: exp_type or type(default_value)
    """

    try:
        # return argument of selected key if valid
        return check_args(kwargs[arg_name], exp_type)
    except KeyError:
        # arg_name is not part of the kwargs keys
        return default_value


def check_kwargs_list(kwargs, arg_name, iterable_type, exp_item_type, default_value):
    """Check the legality of the type of the elements inside the iterable content of a key/argument pair,
    raise ValueError if wrong.

    :param kwargs: keyword-argument dictionary.
    :param arg_name: string containing the name of the argument to check. It's argument **must** be iterable.
    :param iterable_type: iterable type the checked argument should be instance of.
    :param exp_item_type: (list of) expected type(s) of the argument items.
    :param default_value: return this value if the *arg_name* is not found in kwargs (it's type is not checked).

    :type kwargs: dict
    :type arg_name: str
    :type iterable_type: iterable
    :type exp_item_type: any or list of any type
    :type default_value: any

    :return: *kwargs[arg_name]* if type is valid, *default_value* if *arg_name* is not in the *kwargs.keys()*.
    :rtype: exp_type or type(default_value)
    """

    # raise an exception if wrong key/argument pair
    check_kwargs(kwargs, arg_name, iterable_type, default_value)

    try:
        # check argument items
        for item in kwargs[arg_name]:        # raise KeyError if arg_name is not part of the keys
            check_args(item, exp_item_type)  # raise ValueError if one item is not legal

        return kwargs[arg_name]

    except KeyError:
        # arg_name is not part of the kwargs keys
        return default_value


def check_enum(argument, exp_enum):
    """Check the legality of an input argument and raise ValueError if wrong.

    This method is specific for enum as it try to parse the input to the target expected enum.

    :param argument: string or enum input to check.
    :param exp_enum: expected enum class.

    :type argument: any
    :type exp_enum: enum

    :return: *argument* if legal
    :rtype: enum"""

    try:
        return exp_enum(argument)
    except ValueError:
        raise ValueError(
            "Wrong argument type. Given argument '%s' cannot be casted to '%s'" % (argument, exp_enum))


def check_args(argument, exp_type):
    """Check the legality of an input argument and raise ValueError if wrong.

    :param argument: argument value to check.
    :param exp_type: type or list of types accepted for the checked argument.

    :type argument: any
    :type exp_type: any or list of any type

    :return: *argument* if legal.
    :rtype: type(argument)
    """

    # create list of types
    if not isinstance(exp_type, list):
        type_list = []
        type_list.append(exp_type)
    else:
        type_list = exp_type

    # perform check
    if isinstance(argument, tuple(type_list)):
        return argument
    else:
        raise ValueError(
            "Wrong argument type. Expected '%s' found '%s'" % (exp_type, type(argument)))


def check_args_list(argument, iterable_type, exp_item_type):
    """Check the legality of the type of elements inside the iterable argument raise ValueError if wrong.

    :param argument: argument to be checked, **must** be an iterable.
    :param iterable_type: type of the inspected argument.
    :param exp_item_type: (list of) expected type(s) of the argument items.

    :type argument: iterable
    :type iterable_type: iterable
    :type exp_item_type: any or list of any type

    :return: *argument* if it is legal.
    :rtype: type(argument)
    """

    # raise an exception if wrong argument type
    check_args(argument, iterable_type)

    # check argument items
    for item in argument:
        check_args(item, exp_item_type)

    return argument


def get_class_name(obj):
    """Get the class name removing all extra characters ('<', '>', etc..)"""
    return re.search("(?<=').*(?=')", str(type(obj))).group().split('.')[-1]
