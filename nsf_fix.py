import nsf_fix_util as fu
import math
import numpy as np


class FixNum:
    """Fixed point number class

    Round methods:
    SymInf    : positive numbers tends to +inf, negative numbers to -inf
    SymZero   : round toward zero
    NonSymPos : round toward +inf
    NonSymNeg : round toward -inf
    ConvEven  : round to closest even
    ConvOdd   : round to closest odd
    Floor     : round to largest previous
    Ceil      : round to smallest following

    Saturation method
    Sat  : saturate
    Wrap : wrap around

    :param value: value to represent in fix point
    :type value: float
    :param fmt: fix point format
    :type fmt: FixFmt
    :param rnd: round method
    :type rnd: string
    :param over: overflow method
    :type over: string
    :return: fixed point object
    :rtype: NsfFix
    """

    def __init__(self,
                 value,
                 fmt: fu.FixFmt,
                 rnd="NonSymPos",
                 over="Sat"):

        # cast to np is necessary
        if type(value) is not np.ndarray:
            value = np.ndarray(value)  # it might be just a float, hence dim 0

        # make input matrix rank greater than 0
        if value.ndim == 0:
            value = np.ndarray([value])  # ensure 'value' being iterable

        # select array type
        atype = np.int64 if fmt.signed else np.uint64

        # round
        if rnd == "SymInf":
            fixVal = np.array([v*2**fmt.fracBits+0.5 if v > 0 else
                               v*2**fmt.fracBits-0.5 for v in value], atype)
        elif rnd == "SymZero":
            fixVal = np.array([v*2**fmt.fracBits-0.5 if v > 0 else
                               v*2**fmt.fracBits+0.5 for v in value], atype)
        elif rnd == "NonSymPos":
            fixVal = np.array([v*2**fmt.fracBits+0.5 if v > 0 else
                               v*2**fmt.fracBits+0.5 for v in value], atype)
        elif rnd == "NonSymNeg":
            fixVal = np.array([v*2**fmt.fracBits-0.5 if v > 0 else
                               v*2**fmt.fracBits-0.5 for v in value], atype)
        elif rnd == "ConvEven":
            fixVal = np.array([v*2**fmt.fracBits if int(v) % 2 == 0 else
                               v*2**fmt.fracBits+0.5 for v in value], atype)
        elif rnd == "ConvOdd":
            fixVal = np.array([v*2**fmt.fracBits if int(v) % 2 != 0 else
                              v*2**fmt.fracBits+0.5 for v in value], atype)
        elif rnd == "Floor":
            fixVal = np.floor(value)
        elif rnd == "Ceil":
            fixVal = np.ceil(value)
        else:
            raise NameError("###Err###: %r is not valid round value.")

        # check overflow
        if over == "Sat":
            if fmt.signed:
                # fixVal = max(min(fixVal, 2**(fmt.bit_length()-1)-1),
                #              -2**(fmt.bit_length()-1))
                fixVal = np.array(
                    [max(
                        min(f, 2**(fmt.bit_length()-1)-1),
                        -2**(fmt.bit_length()-1)) for f in fixVal], atype)
            else:
                fixVal = np.array([max(
                    min(f, 2**(fmt.bit_length())-1), 0)
                                   for f in fixVal], atype)
        elif over == "Wrap":
            bitSel = 2**(fmt.bit_length())

        self._value = fixVal*2.**(-fmt.fracBits)
        self._fmt = fmt
        self._rnd = rnd
        self._sat = over

    # methods
    def __str__(self):
        return """
        """ + str(self._value) + """
        format: """ + str(self._fmt) + """
        round: """ + self._rnd + """
        saturate: """ + self._sat

    def get_fmt(self):
        return self._fmt

    # operators
    def __add__(self, other):
        return NotImplemented

    def __sub__(self):
        return NotImplemented

    def __mul__(self):
        return NotImplemented
