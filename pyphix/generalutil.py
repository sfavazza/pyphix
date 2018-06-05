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


def check_args(args, exp_type):
    """Check the legality of an input argument and raise ValueError if wrong.

    :param args: argument value to check.
    :param exp_type: type or list of types accepted for the checked argument.

    :type args: any
    :type exp_type: any or list of any type

    :return: *args* if legal.
    :rtype: type(args)
    """

    # create list of types
    if not isinstance(exp_type, list):
        type_list = []
        type_list.append(exp_type)
    else:
        type_list = exp_type

    # perform check
    if isinstance(args, tuple(type_list)):
        return args
    else:
        raise ValueError(f"Wrong argument type. Expected '{exp_type}' found '{type(args)}'")


def check_args_list(args, iterable_type, exp_item_type):
    """Check the legality of the type of elements inside the iterable argument raise ValueError if wrong.

    :param args: argument to be checked, **must** be an iterable.
    :param iterable_type: type of the inspected argument.
    :param exp_item_type: (list of) expected type(s) of the argument items.

    :type args: iterable
    :type iterable_type: iterable
    :type exp_item_type: any or list of any type

    :return: *args* if it is legal.
    :rtype: type(args)
    """

    # raise an exception if wrong argument type
    check_args(args, iterable_type)

    # check argument items
    for item in args:
        check_args(item, exp_item_type)

    return args


def get_class_name(obj):
    return re.search("(?<=').*(?=')", str(type(obj))).group().split('.')[-1]
