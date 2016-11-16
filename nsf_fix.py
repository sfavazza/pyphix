import nsf_fix_util as fu
import numpy as np


class FixNum:
    """Fixed point number class

    Round methods:
    SymInf    : positive numbers tends to +inf, negative numbers to -inf
    SymZero   : round toward zero -- DEFAULT
    NonSymPos : round toward +inf
    NonSymNeg : round toward -inf
    ConvEven  : round to closest even
    ConvOdd   : round to closest odd
    Floor     : round to largest previous
    Ceil      : round to smallest following

    Saturation method
    Sat  : saturate
    Wrap : wrap around -- DEFAULT

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
                 rnd="SymZero",
                 over="Wrap"):

        # cast to np is necessary
        if type(value) is not np.ndarray:
            value = np.array(value) if isinstance(value, list) \
                    else np.array([value])  # prevent 0 dimension array

        # turn input into 1D array (to allow iteration through out all values)
        shape = value.shape
        value = np.reshape(value, -1)
        value = value*2**fmt.fracBits

        # select array type
        atype = np.int64 if fmt.signed else np.uint64

        # round
        if rnd == "SymInf":
            fixVal = np.array([v+.5 if v > 0 else
                               v-.5 for v in value])
        elif rnd == "SymZero":
            fixVal = np.array([v+.4 if v > 0 else
                               v-.4 for v in value])
        elif rnd == "NonSymPos":
            fixVal = np.array([v+.5 if v > 0 else
                               v-.4 for v in value])
        elif rnd == "NonSymNeg":
            fixVal = np.array([v+.4 if v > 0 else
                               v-.5 for v in value])
        elif rnd == "ConvEven":
            fixVal = np.array([v+.4 if (v >= 0) and
                               int(v) % 2 == 0 else
                               v-.4 if (v < 0) and
                               int(v) % 2 == 0 else
                               v+.5 if v > 0 else
                               v-.5 for v in value])
        elif rnd == "ConvOdd":
            fixVal = np.array([v+.5 if (v >= 0) and
                               (int(v) % 2 == 0) else
                               v-.5 if (v < 0) and
                               (int(v) % 2 == 0) else
                               v+.4 if v > 0 else
                               v-.4 for v in value])
        elif rnd == "Floor":
            # not merhely floor function as symmetric in both directions
            fixVal = np.array([int(v) for v in
                               value])
        elif rnd == "Ceil":
            fixVal = np.array([np.ceil(v) for v in value])
        else:
            raise ValueError("_ERROR_: %r is not valid round value." % rnd)

        # check overflow
        if over == "Sat":
            if fmt.signed:
                fixVal = np.array(
                    [max(min(f, fmt.max()), fmt.min()) for f in fixVal], atype)
            else:
                fixVal = np.array([max(
                    min(f, 2**(fmt.bit_length())-1), 0)
                                   for f in fixVal], atype)
        elif over == "Wrap":
            bitSel = 2**(fmt.bit_length())-1
            if fmt.signed:
                compl2s = np.array([int(f) & bitSel for f in fixVal], atype)
                fixVal = np.array([
                    # if non negative
                    int(f) if int(f) & 2**(fmt.bit_length()-1) == 0
                    # if negative make 2's complement and restore negative sign
                    else -((~f + 1) & bitSel) for f in compl2s],
                                  atype)
            else:
                fixVal = np.array([int(f) & bitSel for f in fixVal], atype)
        else:
            raise ValueError("_ERROR_: %r is not valid overflow value." % over)
        # TODO: tackle with negative frac or int bits number in format
        self.value = np.reshape(fixVal*2.**(-fmt.fracBits), shape)
        self.fmt = fmt
        self.rnd = rnd
        self.over = over
        self.shape = shape

    # methods

    def change_fix(self, newFmt, newRnd, newOver):
        '''Return input FixNum object expressed with passed:
        format, round method and overflow method'''
        return FixNum(self.value, newFmt, newRnd, newOver)

    def bin(self):
        tmpVal = np.reshape(self.value, -1) * 2**self.fmt.fracBits
        bitSel = 2**(self.fmt.bit_length())-1
        tmpBin = np.array([bin(np.int(x)) if x >= 0 else
                           bin((~np.int(-x) + 1) & bitSel) for x in tmpVal])
        return np.reshape(tmpBin, self.shape)

    def hex(self):
        return np.array([hex(x) for x in self.int()])

    def int(self):
        tmpVal = np.reshape(self.value, -1) * 2**self.fmt.fracBits
        bitSel = 2**(self.fmt.bit_length())-1
        tmpBin = np.array([np.int(x) if x >= 0 else
                           (~np.int(-x) + 1) & bitSel for x in tmpVal])
        return np.reshape(tmpBin, self.shape)

    def fimath(self):
        """Return fix math as tuple (round method, overflow mode).
        """
        return (self.rnd, self.over)

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

    def __len__(self):
        return len(self.value)

    # operators

    # ## Addition methods

    def __add__(self, other):
        tmpVal = self.value + other.value
        tmpFmt = fu.FixFmt(max(self.fmt.signed, other.fmt.signed),
                           max(self.fmt.intBits, other.fmt.intBits)+1,
                           max(self.fmt.fracBits, other.fmt.fracBits))
        if (self.rnd != other.rnd) or (self.over != other.over):
            print('_WARNING_: operators have round and / or overflow methods \
not equal, those of first operator will be considered')
        return FixNum(tmpVal, tmpFmt, self.rnd, self.over)

    def add(self, other, outFmt=None, outRnd="SymZero", outOver="Wrap"):
        '''
        Addition method.
        It allows to decide output format.
        If not indicated, full-precision format will be adopted
        '''
        tmpVal = self.value + other.value
        tmpFmt = fu.FixFmt(max(self.fmt.signed, other.fmt.signed),
                           max(self.fmt.intBits, other.fmt.intBits)+1,
                           max(self.fmt.fracBits, other.fmt.fracBits)
                           ) if outFmt is None else outFmt
        return FixNum(tmpVal, tmpFmt, outRnd, outOver)

    # ## Subtraction methods

    def __sub__(self, other):
        tmpVal = self.value - other.value
        tmpFmt = fu.FixFmt(max(self.fmt.signed, other.fmt.signed),
                           max(self.fmt.intBits, other.fmt.intBits)+1,
                           max(self.fmt.fracBits, other.fmt.fracBits))
        if (self.rnd != other.rnd) or (self.over != other.over):
            print('_WARNING_: operators have round and / or overflow methods \
not equal, those of first operator will be considered')
        return FixNum(tmpVal, tmpFmt, self.rnd, self.over)

    def sub(self, other, outFmt=None, outRnd="SymZero", outOver="Wrap"):
        '''
        Subtraction method.
        It allows to decide output format.
        If not indicated, full-precision format will be adopted
        '''
        tmpVal = self.value - other.value
        tmpFmt = fu.FixFmt(max(self.fmt.signed, other.fmt.signed),
                           max(self.fmt.intBits, other.fmt.intBits)+1,
                           max(self.fmt.fracBits, other.fmt.fracBits)
                           ) if outFmt is None else outFmt
        return FixNum(tmpVal, tmpFmt, outRnd, outOver)

    # ## Multiplication methods

    def __mul__(self, other):
        tmpVal = self.value * other.value
        tmpSign = max(self.fmt.signed, other.fmt.signed)
        tmpFmt = fu.FixFmt(tmpSign,
                           self.fmt.intBits + other.fmt.intBits + 1 if
                           tmpSign else self.fmt.intBits + other.fmt.intBits,
                           self.fmt.fracBits + other.fmt.fracBits)
        if (self.rnd != other.rnd) or (self.over != other.over):
            print('_WARNING_: operators have round and / or overflow methods \
not equal, those of first operator will be considered')
        return FixNum(tmpVal, tmpFmt, self.rnd, self.over)

    def mult(self, other, outFmt=None, outRnd="SymZero", outOver="Wrap"):
        '''
        Multiplication method.
        It allows to decide output format.
        If not indicated, full-precision format will be adopted
        '''
        tmpVal = self.value * other.value
        tmpSign = max(self.fmt.signed, other.fmt.signed)
        tmpFmt = fu.FixFmt(tmpSign,
                           self.fmt.intBits + other.fmt.intBits + 1 if
                           tmpSign else self.fmt.intBits + other.fmt.intBits,
                           self.fmt.fracBits + other.fmt.fracBits
                           ) if outFmt is None else outFmt
        return FixNum(tmpVal, tmpFmt, outRnd, outOver)

    # ## Negation method

    def __neg__(self):
        return FixNum(-self.value, self.fmt, self.rnd, self.over)
