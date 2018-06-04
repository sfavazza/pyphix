"""Module implementing fix-point arithmentic classes."""

__author__ = "Samuele FAVAZZA"
__copyright__ = "Copyright 2018, Samuele FAVAZZA"

import numpy as np
from numpy import bitwise_and as np_and
from numpy import bitwise_not as np_not

from . import generalutil as gu


class FixFmt:
    """Fix format class

    :param signed: indicate whether the representation is signed (True) or unsigned
    :param int_bits: number of bits representing the integer part
    :param frac_bits: number of bits representing the fractional part

    :type signed: bool
    :type int_bits: int
    :type frac_bits: int
    """

    def __init__(self, signed, int_bits, frac_bits):

        if int_bits < 0 or frac_bits < 0:
            raise ValueError("Integer and fractional sizes must be positive.")

        self.signed = gu.check_args(signed, bool)
        self.int_bits = gu.check_args(int_bits, int)
        self.frac_bits = gu.check_args(frac_bits, int)

    def __str__(self):
        return f"({self.signed}, {self.int_bits}, {self.frac_bits})"

    def __repr__(self):
        return f"""{self.__str__()}
<{gu.get_class_name(self)} at {hex(id(self))}>"""

    @property
    def bit_length(self):
        """Return the number of bits required to represent a number with current fix format."""
        return int(self.signed) + self.int_bits + self.frac_bits

    @property
    def maxvalue(self):
        """Return max representable value by current fix format objext."""
        toRealCoeff = (1 << self.frac_bits)
        if self.signed:
            return ((1 << (self.bit_length-1))-1)/toRealCoeff
        return ((1 << (self.bit_length))-1)/toRealCoeff

    @property
    def minvalue(self):
        """Return min representable value by current fix format objext."""
        if self.signed:
            return -2**(self.bit_length-1)/2**self.frac_bits
        return 0

    @property
    def range(self):
        """Return the range representable by fix format object as tuple (min, max)."""
        return (self.minvalue, self.maxvalue)

    @property
    def tuplefmt(self):
        """Return object as a tuple."""
        return (self.signed,
                self.int_bits,
                self.frac_bits)

    @property
    def listfmt(self):
        """Return object as a list."""
        return [self.signed,
                self.int_bits,
                self.frac_bits]


class FixNum:
    """Fixed point number class

    =============
    Round methods
    =============
    ``SymInf``    : positive numbers tends to +inf, negative numbers to -inf
    ``SymZero``   : round toward zero -- DEFAULT
    ``NonSymPos`` : round toward +inf
    ``NonSymNeg`` : round toward -inf
    ``ConvEven``  : round to closest even
    ``ConvOdd``   : round to closest odd
    ``Floor``     : round to largest previous
    ``Ceil``      : round to smallest following

    ==================
    Saturation methods
    ==================
    ``Sat``  : saturate
    ``Wrap`` : wrap around -- DEFAULT

    :param value: value to represent in fix point
    :param fmt: fix point format
    :param rnd: round method
    :param over: overflow method

    :type value: np.ndarray(ndim > 0) or float
    :type fmt: FixFmt
    :type rnd: string
    :type over: string
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

        # always cast to np.float64
        try:
            # turn into array
            self.value, self.shape = self._toIndexableArray(value)
            # round and overflow process in int format
            self.value = self._over(self._round(self.value*self.to_int_coeff))

            # back to float
            self.value = self.value/self.to_int_coeff

        except ValueError:
            print('Wrong input value type, only numeric list/np.arrays are allowed')
            raise

    # support methods
    def _valueToLine(self, value):
        """Turn input value into vector form"""
        return np.reshape(value, -1)

    def _tmpInt(self):
        """Geneate integer representation of the fix object"""
        tmp_value = self._valueToLine(self.value) * 2**self.fmt.frac_bits
        return np.array([np.int(x) if x >= 0 else
                         (np.int(x) & self._fix_size_mask) for x in tmp_value])

    def _toIndexableArray(self, value):
        """Turn input value into an indexable array.
        Return a tuple (value, shape)"""
        # turn into array
        value = np.array(value, dtype=np.float64)
        shape = (1, ) if value.shape is () else value.shape
        # ensure also single values are indexable
        return (np.reshape(value, shape), shape)

    # private methods
    def _round(self, value):
        """Perform specified rounding on input values

        value : it must be an indexable vector (even when a single number is provided)
        """
        if self.rnd == "SymInf":
            value[value > 0] += .5
            value[value < 0] -= .5
        elif self.rnd == "SymZero":
            value[value > 0] += .4
            value[value < 0] -= .4
        elif self.rnd == "NonSymPos":
            value[value > 0] += .5
            value[value < 0] -= .4
        elif self.rnd == "NonSymNeg":
            value[value > 0] += .4
            value[value < 0] -= .5
        elif self.rnd in ["ConvEven", "ConvOdd"]:
            evenSel, oddSel = value.astype(int) % 2 == 0, value.astype(int) % 2 != 0
            # even
            value[np.logical_and(evenSel, value > 0)] += .4 if self.rnd == "ConvEven" else .5
            value[np.logical_and(evenSel, value < 0)] -= .4 if self.rnd == "ConvEven" else .5
            # odd
            value[np.logical_and(oddSel, value > 0)] += .5 if self.rnd == "ConvEven" else .4
            value[np.logical_and(oddSel, value < 0)] -= .5 if self.rnd == "ConvEven" else .4
        elif self.rnd == "Floor":
            # round to the previous largest
            value = np.floor(value)
        elif self.rnd == "Ceil":
            # round to the next smallest
            value = np.ceil(value)
        else:
            raise ValueError("_ERROR_: %r is not valid round value." % self.rnd)
        # convert to integer
        return value.astype(int)

    def _over(self, value):
        """Implement specified overflow method on input value"""
        if self.over == "Sat":
            value = np.maximum(
                np.minimum(value, self.fmt.maxvalue*self.to_int_coeff),
                self.fmt.minvalue*self.to_int_coeff)
        elif self.over == "Wrap":
            # selection masks
            highBitMask = (1 << (self.fmt.bit_length-1))
            # pos / neg selector
            value = np_and(value, self._fix_size_mask)
            posSel = np_and(value, highBitMask) == 0
            negSel = np.logical_not(posSel)
            if self.fmt.signed:
                # non negative
                value[posSel] = value[posSel]
                # negative
                value[negSel] = -np_and((np_not(value[negSel]) + 1), self._fix_size_mask)
        else:
            raise ValueError("_ERROR_: %r is not valid overflow value." % self.over)

        return value

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
        tmp_bin = np.array([bin(x) for x in self._tmpInt()])
        # correct string representation
        tmp_bin = np.array(['0b' + (self.fmt.bit_length - len(x[2:])) * '0' + x[2:] for x in tmp_bin])
        return np.reshape(tmp_bin, self.shape)

    @property
    def hex(self):
        tmp_hex = np.array([hex(x) for x in self._valueToLine(self.int)])
        # correct string representation
        tmp_hex = np.array(['0x' + (int(np.ceil(self.fmt.bit_length / 4)) - len(x[2:])) * '0' + x[2:]
                            for x in tmp_hex])
        return np.reshape(tmp_hex, self.shape)

    @property
    def int(self):
        return np.reshape(self._tmpInt(), self.shape)

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

    def __getitem__(self, idx):
        return FixNum(self.value[idx], self.fmt, self.rnd, self.over)

    def __setitem__(self, idx, repleaceValue):
        if isinstance(repleaceValue, FixNum):
            self.value[idx] = self._over(self._round(
                self._toIndexableArray(repleaceValue.value)[0]*self.to_int_coeff))/self.to_int_coeff
        else:
            self.value[idx] = self._over(self._round(
                self._toIndexableArray(repleaceValue)[0]*self.to_int_coeff))/self.to_int_coeff

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
