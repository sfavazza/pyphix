"""Module implementing fix-point arithmentic classes
"""
# for decorator
import time
# imports for module
from copy import copy
import numpy as np
from numpy import bitwise_and as np_and
from numpy import bitwise_not as np_not
import pdb


# function performance decorator
def time_perfomance(func):
    """Decorate methods to estimate their time performance"""

    def function_exec_time_wrapper(*args, **kwargs):
        """Estimate time implied to run given function"""
        start_time = time.time()
        function_object = func(*args, **kwargs)
        end_time = time.time()
        print(f'Time to run function {func.__name__}: {end_time - start_time}')
        return function_object

    return function_exec_time_wrapper


class FixFmt:
    """Fix format class
    """

    def __init__(self,
                 signed: bool,
                 int_bits,
                 frac_bits):

        if not isinstance(signed, bool):
            raise TypeError("_ERROR_: sign of format must be bool")

        if int_bits + frac_bits <= 0:
            raise ValueError("_ERROR_: sum of integer and fractional bits has to be positive")

        self.signed = signed
        self.int_bits = int_bits
        self.frac_bits = frac_bits

    def __str__(self):
        return "(" + str(self.signed) + "," + str(self.int_bits) + "," + str(self.frac_bits) + ")"

    def __repr__(self):
        return """(""" + str(self.signed) + "," + str(self.int_bits) + "," + str(self.frac_bits) + """)
""" + "<nsf_fix_util.FixFmt at " + hex(id(self)) + '>'

    @property
    def bit_length(self):
        """Return the number of bits required to represent a number with current fix format"""
        return int(self.signed) + self.int_bits + self.frac_bits

    @property
    def max(self):
        """Return max representable value by current fix format objext
        """
        toRealCoeff = (1 << self.frac_bits)
        if self.signed:
            return ((1 << (self.bit_length-1))-1)/toRealCoeff
        return ((1 << (self.bit_length))-1)/toRealCoeff

    @property
    def min(self):
        """Return min representable value by current fix format objext
        """
        if self.signed:
            return -2**(self.bit_length-1)/2**self.frac_bits
        return 0

    @property
    def range(self):
        """Return the range representable by fix format object as tuple (min, max)
        """
        return (self.max, self.min)

    @property
    def tuple(self):
        """Return object as a tuple.
        """
        return (self.signed,
                self.int_bits,
                self.frac_bits)

    @property
    def list(self):
        """Return object as a list.
        """
        return [self.signed,
                self.int_bits,
                self.frac_bits]


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

    Saturation methods
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
                 fmt: FixFmt,
                 rnd="SymZero",
                 over="Wrap"):

        # init instance members
        self.fmt = fmt
        self.rnd = rnd
        self.over = over
        self._index = 0

        # internal constants
        self.to_int_coeff = 2**self.fmt.frac_bits  # to integer representation coefficient
        self._fix_size_mask = (1 << self.fmt.bit_length)-1  # correct representation

        # always cast to float64
        try:
            value = np.array(value, dtype=np.float64)

            # turn input into 1D array (to allow iteration through out all values)
            self.shape = value.shape
            # round
            self._round()

            # check overflow
            self._over(toIntCoeff)
            # TODO: tackle with negative frac or negative int bits number in format
            self.value = np.reshape(self.value/toIntCoeff, self.shape)

        except ValueError:
            print('Wrong input value type, only numeric list/np.arrays are allowed')
            raise

    # private methods
    def _round(self):
        """Perform specified rounding on input values"""
        if self.rnd == "SymInf":
            self.value[self.value > 0] += .5
            self.value[self.value < 0] -= .5
        elif self.rnd == "SymZero":
            self.value[self.value > 0] += .4
            self.value[self.value < 0] -= .4
        elif self.rnd == "NonSymPos":
            self.value[self.value > 0] += .5
            self.value[self.value < 0] -= .4
        elif self.rnd == "NonSymNeg":
            self.value[self.value > 0] += .4
            self.value[self.value < 0] -= .5
        elif self.rnd in ["ConvEven", "ConvOdd"]:
            evenSel, oddSel = self.value.astype(int) % 2 == 0, self.value.astype(int) % 2 != 0
            # even
            self.value[np.logical_and(evenSel, self.value > 0)] += .4 if self.rnd == "ConvEven" else .5
            self.value[np.logical_and(evenSel, self.value < 0)] -= .4 if self.rnd == "ConvEven" else .5
            # odd
            self.value[np.logical_and(oddSel, self.value > 0)] += .5 if self.rnd == "ConvEven" else .4
            self.value[np.logical_and(oddSel, self.value < 0)] -= .5 if self.rnd == "ConvEven" else .4
        elif self.rnd == "Floor":
            # round to the previous largest
            self.value = np.floor(self.value)
        elif self.rnd == "Ceil":
            # round to the next smallest
            self.value = np.ceil(self.value)
        else:
            raise ValueError("_ERROR_: %r is not valid round value." % self.rnd)
        # convert to integer
        self.value = self.value.astype(int)

    def _over(self, toIntCoeff):
        """Implement specified overflow method on input value"""
        if self.over == "Sat":
            self.value = np.maximum(
                np.minimum(self.value, self.fmt.max*toIntCoeff),
                self.fmt.min*toIntCoeff)
        elif self.over == "Wrap":
            # selection masks
            highBitMask = (1 << (self.fmt.bit_length-1))
            # pos / neg selector
            self.value = np_and(self.value, self._fixSizeMask)
            posSel = np_and(self.value, highBitMask) == 0
            negSel = np.logical_not(posSel)
            if self.fmt.signed:
                # non negative
                self.value[posSel] = self.value[posSel]
                # negative
                self.value[negSel] = -np_and((np_not(self.value[negSel]) + 1), self._fixSizeMask)
        else:
            raise ValueError("_ERROR_: %r is not valid overflow value." % self.over)

    # public methods
    def change_fix(self,
                   new_fmt: FixFmt,
                   new_rnd: str = None,
                   new_over: str = None):
        """Change fix parameters of current object.
        WARNING: this action may lead to information loss due to new format and round/overflow methods.

        :param new_fmt: new format (mandatory)
        :param new_rnd: new round method, if not specified current is used
        :param new_over: new saturation method, if not specified current is used
        """
        return FixNum(self.value, new_fmt,
                      self.rnd if new_rnd is None else new_rnd,
                      self.over if new_over is None else new_over)

    @property
    def bin(self):
        tmpVal = np.reshape(self.value, -1) * 2**self.fmt.frac_bits
        tmpBin = np.array([bin(np.int(x)) if x >= 0 else
                           bin((~np.int(-x) + 1) & self._fixSizeMask) for x in tmpVal])
        return np.reshape(tmpBin, self.shape)

    @property
    def hex(self):
        return np.array([hex(x) for x in self.int()])

    @property
    def int(self):
        tmpVal = np.reshape(self.value, -1) * 2**self.fmt.frac_bits
        tmpBin = np.array([np.int(x) if x >= 0 else
                           (~np.int(-x) + 1) & self._fixSizeMask for x in tmpVal])
        return np.reshape(tmpBin, self.shape)

    @property
    def fimath(self):
        """Return fix math as tuple (round method, overflow mode).
        """
        return (self.rnd, self.over)

    # data model
    # # representation
    def __str__(self):
        return """
        """ + str(self.value) + """
        fmt: """ + str(self.fmt) + """
        rnd: """ + self.rnd + """ over: """ + self.over

    def __repr__(self):
        return """
        """ + str(self.value) + """
        fmt: """ + str(self.fmt) + """
        rnd: """ + self.rnd + """ over: """ + self.over + """

        <nsf_fix.FixNum at """ + hex(id(self)) + '>'

    # # container methods
    def __contains__(self, elem):
        if isinstance(elem, FixNum):
            return elem.value in self.value
        return elem in self.value

    def __getitem__(self, k):
        sliced = copy(self)
        sliced.value = self.value[k]
        return sliced

    def __setitem__(self, k, repleaceValue):
        if isinstance(repleaceValue, FixNum):
            self.value[k] = repleaceValue.value
        else:
            self.value[k] = repleaceValue

    def __len__(self):
        return self.shape

    # # generator
    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        try:
            ret = FixNum(self.value[self._index], self.fmt, self.rnd, self.over)
            self._index += 1
        except IndexError:
            raise StopIteration
        return ret

    # # operators
    # ## Addition methods
    def __add__(self, other):
        """x + y --> x.__add__(y)"""
        tmpVal = self.value + other.value
        tmpFmt = FixFmt(max(self.fmt.signed, other.fmt.signed),
                        max(self.fmt.int_bits, other.fmt.int_bits)+1,
                        max(self.fmt.frac_bits, other.fmt.frac_bits))
        if (self.rnd != other.rnd) or (self.over != other.over):
            print('_WARNING_: operators have round and/or overflow methods ' +
                  'not equal, those of first operator will be considered')
        return FixNum(tmpVal, tmpFmt, self.rnd, self.over)

    def add(self, other, outFmt=None, outRnd="SymZero", outOver="Wrap"):
        """
        Addition method.
        It allows to decide output format.
        If not indicated, full-precision format will be adopted
        """
        tmpVal = self.value + other.value
        tmpFmt = FixFmt(max(self.fmt.signed, other.fmt.signed),
                        max(self.fmt.int_bits, other.fmt.int_bits)+1,
                        max(self.fmt.frac_bits, other.fmt.frac_bits)) if outFmt is None else outFmt
        return FixNum(tmpVal, tmpFmt, outRnd, outOver)

    # ## Subtraction methods
    def __sub__(self, other):
        tmpVal = self.value - other.value
        tmpFmt = FixFmt(max(self.fmt.signed, other.fmt.signed),
                        max(self.fmt.int_bits, other.fmt.int_bits)+1,
                        max(self.fmt.frac_bits, other.fmt.frac_bits))
        if (self.rnd != other.rnd) or (self.over != other.over):
            print('_WARNING_: operators have round and / or overflow methods ' +
                  'not equal, those of first operator will be considered')
        return FixNum(tmpVal, tmpFmt, self.rnd, self.over)

    def sub(self, other, outFmt=None, outRnd="SymZero", outOver="Wrap"):
        """
        Subtraction method.
        It allows to decide output format.
        If not indicated, full-precision format will be adopted
        """
        tmpVal = self.value - other.value
        tmpFmt = FixFmt(max(self.fmt.signed, other.fmt.signed),
                        max(self.fmt.int_bits, other.fmt.int_bits)+1,
                        max(self.fmt.frac_bits, other.fmt.frac_bits)) if outFmt is None else outFmt
        return FixNum(tmpVal, tmpFmt, outRnd, outOver)

    # ## Multiplication methods
    def __mul__(self, other):
        tmpVal = self.value * other.value
        tmpSign = max(self.fmt.signed, other.fmt.signed)
        tmpFmt = FixFmt(tmpSign,
                        self.fmt.int_bits + other.fmt.int_bits + 1 if
                        tmpSign else self.fmt.int_bits + other.fmt.int_bits,
                        self.fmt.frac_bits + other.fmt.frac_bits)
        if (self.rnd != other.rnd) or (self.over != other.over):
            print('_WARNING_: operators have round and / or overflow methods ' +
                  'not equal, those of first operator will be considered')
        return FixNum(tmpVal, tmpFmt, self.rnd, self.over)

    def mult(self, other, outFmt=None, outRnd="SymZero", outOver="Wrap"):
        """
        Multiplication method.
        It allows to decide output format.
        If not indicated, full-precision format will be adopted
        """
        tmpVal = self.value * other.value
        tmpSign = max(self.fmt.signed, other.fmt.signed)
        tmpFmt = FixFmt(tmpSign,
                        self.fmt.int_bits + other.fmt.int_bits + 1 if
                        tmpSign else self.fmt.int_bits + other.fmt.int_bits,
                        self.fmt.frac_bits + other.fmt.frac_bits) if outFmt is None else outFmt
        return FixNum(tmpVal, tmpFmt, outRnd, outOver)

    # ## Negation method
    def __neg__(self):
        return FixNum(-self.value, self.fmt, self.rnd, self.over)

    # ## Comparison methods
    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other
