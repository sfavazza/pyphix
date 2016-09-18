import nsf_fix_util as fu
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
    :type value: np.ndarray(ndim > 0), float
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
            value = np.array(value) if isinstance(value, list) \
                    else np.array([value])  # prevent 0 dimension array

        # turn input into 1D array (to allow iteration through out all values)
        shape = value.shape
        value = np.reshape(value, -1)

        # select array type
        atype = np.int64 if fmt.signed else np.uint64

        # round
        if rnd == "SymInf":
            fixVal = np.array([v*2**fmt.fracBits+0.5 if v > 0 else
                               v*2**fmt.fracBits-0.5 for v in value])
        elif rnd == "SymZero":
            fixVal = np.array([v*2**fmt.fracBits-0.5 if v > 0 else
                               v*2**fmt.fracBits+0.5 for v in value])
        elif rnd == "NonSymPos":
            fixVal = np.array([v*2**fmt.fracBits+0.5 if v > 0 else
                               v*2**fmt.fracBits+0.5 for v in value])
        elif rnd == "NonSymNeg":
            fixVal = np.array([v*2**fmt.fracBits-0.5 if v > 0 else
                               v*2**fmt.fracBits-0.5 for v in value])
        elif rnd == "ConvEven":
            fixVal = np.array([v*2**fmt.fracBits if int(v) % 2 == 0 else
                               v*2**fmt.fracBits+0.5 for v in value])
        elif rnd == "ConvOdd":
            fixVal = np.array([v*2**fmt.fracBits if int(v) % 2 != 0 else
                               v*2**fmt.fracBits+0.5 for v in value])
        elif rnd == "Floor":
            fixVal = np.array([np.floor(v*2**fmt.fracBits) for v in
                               value], atype)
        elif rnd == "Ceil":
            fixVal = np.array([np.ceil(v*2**fmt.fracBits) for v in value])
        else:
            raise NameError("###Err###: %r is not valid round value." % rnd)

        # check overflow
        if over == "Sat":
            if fmt.signed:
                fixVal = np.array(
                    [max(
                        min(f, 2**(fmt.bit_length()-1)-1),
                        -2**(fmt.bit_length()-1)) for f in fixVal], atype)
            else:
                fixVal = np.array([max(
                    min(f, 2**(fmt.bit_length())-1), 0)
                                   for f in fixVal], atype)
        elif over == "Wrap":
            bitSel = 2**(fmt.bit_length())-1
            fixVal = np.array([int(f) & bitSel for f in fixVal], atype)
        else:
            raise NameError("###Err###: %r is not valid overflow value."
                            % over)

        self.value = np.reshape(fixVal*2.**(-fmt.fracBits), shape)
        self.fmt = fmt
        self.rnd = rnd
        self.over = over

    # methods
    def __str__(self):
        return """
        """ + str(self.value) + """
        format: """ + str(self.fmt) + """
        round: """ + self.rnd + """
        saturate: """ + self.over

    def __repr__(self):
        return """
        """ + str(self.value) + """
        format: """ + str(self.fmt) + """
        round: """ + self.rnd + """
        saturate: """ + self.over + """

        <nsf_fix.FixNum at """ + hex(id(self)) + '>'

    def get_fmt(self):
        return self.fmt

    # operators
    def __add__(self, other):
        return NotImplemented

    def __sub__(self):
        return NotImplemented

    def __mul__(self):
        return NotImplemented
