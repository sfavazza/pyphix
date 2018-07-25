"""Module implementing fix-point arithmentic classes."""

__author__ = "Samuele FAVAZZA"
__copyright__ = "Copyright 2018, Samuele FAVAZZA"

from enum import Enum

import numpy as np
from numpy import bitwise_and as np_and
from numpy import bitwise_not as np_not

from . import generalutil as gu


class EFormat(Enum):
    """Enum class to express number base expression"""
    HEX = 'hex'
    INT = 'int'
    BIN = 'bin'
    FLOAT = 'float'


class ERoundMethod(Enum):
    """Enum class for round methods."""
    SYM_INF = 'SymInf'
    SYM_ZERO = 'SymZero'
    NON_SYM_POS = 'NonSymPos'
    NON_SYM_NEG = 'NonSymNeg'
    CONV_EVEN = 'ConvEven'
    CONV_ODD = 'ConvOdd'
    FLOOR = 'Floor'
    CEIL = 'Ceil'


class EOverMethod(Enum):
    """Enum class for overflow methods."""
    SAT = 'Sat'
    WRAP = 'Wrap'


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
        return "(%s, %s, %s)" % (self.signed, self.int_bits, self.frac_bits)

    def __repr__(self):
        return """%s

  <%s at %s>""" % (self.__str__(), gu.get_class_name(self), hex(id(self)))

    @property
    def mask(self):
        """Return mask to limit number representation (bit_length*ones).

        Ex:

        >>> from pyphix import fix
        >>> fmt = fix.FixFmt(True, 2, 3)
        >>> bin(fmt.mask)
            '0b111111'

        >>> fmt = fix.FixFmt(False, 1, 12)
        >>> bin(fmt.mask)
            '0b1111111111111'"""

        return 2**self.bit_length-1

    @property
    def bit_length(self):
        """Return the number of bits required to represent a number with current fix format."""
        return int(self.signed) + self.int_bits + self.frac_bits

    def _minmaxvalueformatter(self, value, fmt):
        """Return value in desired expressed format.

        :param value: value to format.
        :param fmt: desired format

        :type value: int
        :type fmt: EFormat

        :return: formatted input value.
        :rtype: float or int or str"""

        if fmt is EFormat.BIN:
            return _bin2fixstring(value & self.mask, self.bit_length)

        if fmt is EFormat.HEX:
            return hex(value & self.mask)

        if fmt is EFormat.FLOAT:
            return value/2**self.frac_bits

        return value

    def maxvalue(self, fmt='float'):
        """Return max representable value by current fix format objext.

        :param fmt: format the value is presented, either hex, int, bin, float.

        :type fmt: EFormat or str

        :return: max representable value.
        :rtype: float or int or str"""

        # ensure the given fmt is correct
        _fmt = gu.check_enum(fmt, EFormat)
        maxvalue_int = (1 << (self.bit_length-1))-1 if self.signed else \
                       (1 << (self.bit_length))-1

        return self._minmaxvalueformatter(maxvalue_int, _fmt)

    def minvalue(self, fmt='float'):
        """Return min representable value by current fix format objext."""

        # ensure the given fmt is correct
        _fmt = gu.check_enum(fmt, EFormat)
        minvalue_int = -2**(self.bit_length-1) if self.signed else 0

        return self._minmaxvalueformatter(minvalue_int, _fmt)

    @property
    def fixrange(self):
        """Return the range representable by fix format object as tuple (min, max)."""

        return (self.minvalue(), self.maxvalue())

    @property
    def tuplefmt(self):
        """Return object as a tuple."""

        return (self.signed, self.int_bits, self.frac_bits)

    @property
    def listfmt(self):
        """Return object as a list."""

        return [self.signed, self.int_bits, self.frac_bits]

    def __contains__(self, elem):
        return self.minvalue() <= elem <= self.maxvalue()


class FixNum:
    """Fixed point number class

    +--------------------------------------------------------------------------+
    | **Round methods**                                                        |
    +---------------+----------------------------------------------------------+
    | ``SymInf``    | positive numbers tend to +inf, negative numbers to -inf  |
    +---------------+----------------------------------------------------------+
    | ``SymZero``   | round toward zero (*DEFAULT*)                            |
    +---------------+----------------------------------------------------------+
    | ``NonSymPos`` | round toward +inf                                        |
    +---------------+----------------------------------------------------------+
    | ``NonSymNeg`` | round toward -inf                                        |
    +---------------+----------------------------------------------------------+
    | ``ConvEven``  | round to closest even                                    |
    +---------------+----------------------------------------------------------+
    | ``ConvOdd``   | round to closest odd                                     |
    +---------------+----------------------------------------------------------+
    | ``Floor``     | round to largest previous                                |
    +---------------+----------------------------------------------------------+
    | ``Ceil``      | round to smallest following                              |
    +---------------+----------------------------------------------------------+

    +-------------------------------------------+
    | **Overflow methods**                      |
    +------------------+------------------------+
    | ``Sat``          | saturate               |
    +------------------+------------------------+
    | ``Wrap``         | wrap around -- DEFAULT |
    +------------------+------------------------+

    :param value: value to represent in fix point
    :param fmt: fix point format
    :param rnd: round method
    :param over: overflow method

    :type value: np.ndarray(ndim > 0) or float
    :type fmt: FixFmt
    :type rnd: str
    :type over: str
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, value, fmt, rnd="SymZero", over="Wrap"):

        # init instance members
        self.fmt = gu.check_args(fmt, FixFmt)
        self.rnd = gu.check_enum(rnd, ERoundMethod)
        self.over = gu.check_enum(over, EOverMethod)
        self._index = 0         # for generator feature

        # internal constants
        self._to_int_coeff = 2**self.fmt.frac_bits  # to integer representation coefficient
        self._fix_size_mask = (1 << self.fmt.bit_length)-1  # correct representation

        # always cast to np.float64
        try:
            # turn into array
            self.value, self.shape = self._to_array(value)
            # round and overflow process in int format
            self.value = self._over(self._round(self.value*self._to_int_coeff))

            # back to float
            self.value = self.value/self._to_int_coeff

        except ValueError:
            print('Wrong input value type, only numeric list/np.arrays are allowed')
            raise

    # support methods
    @staticmethod
    def _value2line(value):
        """Turn input value into vector form."""

        return np.reshape(value, -1)

    def _tmp_int(self):
        """Geneate integer representation of the fix object."""

        tmp_value = self._value2line(self.value) * 2**self.fmt.frac_bits
        return np.array([np.int(x) if x >= 0 else
                         (np.int(x) & self._fix_size_mask) for x in tmp_value])

    @staticmethod
    def _to_array(value):
        """Turn input value into an array even when a simple number.

        :param value: single number or vector.

        :type value: numpy.ndarray or float

        :return: tuple in the form (value, shape), where value is always indexable.
        :rtype: tuple[numpy.ndarray, tuple]"""

        # turn into array
        value = np.array(value, dtype=np.float64)  # pylint: disable=no-member
        shape = value.shape if value.shape else (1, )
        # ensure also single values are indexable
        return (np.reshape(value, shape), shape)

    # private methods
    def _round(self, value):
        """Round input using object rounding method.

        :param value: an indexable object.

        :type value: numpy.ndarray

        :return: rounded value.
        :rtype: numpy.ndarray
        """

        if self.rnd is ERoundMethod.SYM_INF:
            value[value > 0] += .5
            value[value < 0] -= .5
        elif self.rnd is ERoundMethod.SYM_ZERO:
            value[value > 0] += .4
            value[value < 0] -= .4
        elif self.rnd is ERoundMethod.NON_SYM_POS:
            value[value > 0] += .5
            value[value < 0] -= .4
        elif self.rnd is ERoundMethod.NON_SYM_NEG:
            value[value > 0] += .4
            value[value < 0] -= .5
        elif self.rnd in [ERoundMethod.CONV_EVEN, ERoundMethod.CONV_ODD]:
            even_sel, odd_sel = value.astype(int) % 2 == 0, value.astype(int) % 2 != 0
            # even
            value[np.logical_and(even_sel, value > 0)] += .4 if self.rnd is ERoundMethod.CONV_EVEN else .5
            value[np.logical_and(even_sel, value < 0)] -= .4 if self.rnd is ERoundMethod.CONV_EVEN else .5
            # odd
            value[np.logical_and(odd_sel, value > 0)] += .5 if self.rnd is ERoundMethod.CONV_EVEN else .4
            value[np.logical_and(odd_sel, value < 0)] -= .5 if self.rnd is ERoundMethod.CONV_EVEN else .4
        elif self.rnd is ERoundMethod.FLOOR:
            # round to the previous largest
            value = np.floor(value)
        elif self.rnd is ERoundMethod.CEIL:
            # round to the next smallest
            value = np.ceil(value)
        else:
            raise ValueError("_ERROR_: %r is not valid round value." % self.rnd)
        # convert to integer
        return value.astype(int)

    def _over(self, value):
        """Apply current object overflow method on input value.

        :param value: current object value.

        :type value: numpy.ndarray or float

        :return: overflowed value.
        :rtype: numpy.ndarray or float"""

        if self.over is EOverMethod.SAT:
            value = np.maximum(
                np.minimum(value, self.fmt.maxvalue(fmt=EFormat.INT)),
                self.fmt.minvalue(fmt=EFormat.INT))
        elif self.over is EOverMethod.WRAP:
            # selection masks
            high_bit_mask = (1 << (self.fmt.bit_length-1))
            # pos / neg selector
            value = np_and(value, self._fix_size_mask)
            pos_sel = np_and(value, high_bit_mask) == 0
            neg_sel = np.logical_not(pos_sel)
            if self.fmt.signed:
                # non negative
                value[pos_sel] = value[pos_sel]
                # negative
                value[neg_sel] = -np_and((np_not(value[neg_sel]) + 1), self._fix_size_mask)
        else:
            raise ValueError("_ERROR_: %r is not valid overflow value." % self.over)

        return value

    # public methods
    def change_fix(self, new_fmt, new_rnd=None, new_over=None):
        """Change fix parameters of current object.

        **WARNING**: this action may lead to information loss due to new format and round/overflow methods.

        :param new_fmt: new format (mandatory).
        :param new_rnd: new round method, if not specified current is used.
        :param new_over: new saturation method, if not specified current is used.

        :type new_fmt: FixFmt
        :type new_rnd: str or None
        :type new_over: str or None

        :return: new formatted fix-point object.
        :rtype: FixFmt
        """

        return FixNum(self.value, new_fmt,
                      self.rnd if new_rnd is None else new_rnd,
                      self.over if new_over is None else new_over)

    @property
    def binfmt(self):
        """Represent fix-point object in binary format."""

        # correct string representation
        tmp_bin = np.array([_bin2fixstring(x, self.fmt.bit_length) for x in self._tmp_int()])
        return np.reshape(tmp_bin, self.shape)

    @property
    def hexfmt(self):
        """Represent fix-point object in hexadecimal format."""

        tmp_hex = np.array([hex(x) for x in self._value2line(self.intfmt)])
        # correct string representation
        tmp_hex = np.array(['0x' + (int(np.ceil(self.fmt.bit_length / 4)) - len(x[2:])) * '0' + x[2:]
                            for x in tmp_hex])
        return np.reshape(tmp_hex, self.shape)

    @property
    def intfmt(self):
        """Represent fix-point object in integer format."""

        return np.reshape(self._tmp_int(), self.shape)

    @property
    def fimath(self):
        """Return fix math as tuple (round method, overflow mode)."""

        return (self.rnd, self.over)

    # data model
    # # representation
    def __str__(self):
        return """
%s

  fmt: %s
  rnd: %s
  over: %s""" % (self.value, self.fmt, self.rnd, self.over)

    def __repr__(self):
        return """%s

  <%s at %s>""" % (self.__str__(), gu.get_class_name(self), hex(id(self)))

    # # container methods
    def __contains__(self, elem):
        if isinstance(elem, FixNum):
            return elem.value in self.value
        return elem in self.value

    def __getitem__(self, idx):
        return FixNum(self.value[idx], self.fmt, self.rnd, self.over)

    def __setitem__(self, idx, repleace_value):
        if isinstance(repleace_value, FixNum):
            self.value[idx] = self._over(self._round(
                self._to_array(repleace_value.value)[0]*self._to_int_coeff))/self._to_int_coeff
        else:
            self.value[idx] = self._over(self._round(
                self._to_array(repleace_value)[0]*self._to_int_coeff))/self._to_int_coeff

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
    @staticmethod
    def _op_out_casting(op, other, out_fmt=None, out_rnd="SymZero", out_over="Wrap"):
        """Implement format and fimath casting on defualt operations.

        :param op: operation function name (__add__, __sub__, etc...).
        :param other: fix-point object.
        :param out_fmt: optional format operation result can be casted to.
        :param out_rnd: round method adopted on result (default ```SymZero```).
        :param out_over: overflow method adopted on result (default ```Wrap```).

        :type op: method
        :type other: FixNum
        :type out_fmt: FixFmt
        :type out_rnd: str
        :type out_over: str

        :return: addition result.
        :rtype: FixNum"""

        tmp_fix = op(other)
        tmp_fmt = tmp_fix.fmt if out_fmt is None else out_fmt

        return tmp_fix.change_fix(tmp_fmt, out_rnd, out_over)

    # ## Addition methods
    def __add__(self, other):
        """x + y --> x.__add__(y)"""

        tmp_val = self.value + other.value
        tmp_fmt = FixFmt(self.fmt.signed or other.fmt.signed,
                         max(self.fmt.int_bits, other.fmt.int_bits)+1,
                         max(self.fmt.frac_bits, other.fmt.frac_bits))
        if (self.rnd != other.rnd) or (self.over != other.over):
            print('_WARNING_: operators have round and/or overflow methods ' +
                  'not equal, those of first operator will be considered')
        return FixNum(tmp_val, tmp_fmt, self.rnd, self.over)

    def add(self, *args, **kwargs):
        """Addition method.

        *Usage: add(other, out_fmt=None, out_rnd="SymZero", out_over="Wrap")*

        It allows to decide the output format.
        If not indicated, full-precision format will be adopted.

        :param other: fix-point object.
        :param out_fmt: optional format operation result can be casted to.
        :param out_rnd: round method adopted on result (default ```SymZero```).
        :param out_over: overflow method adopted on result (default ```Wrap```).

        :type other: FixNum
        :type out_fmt: FixFmt
        :type out_rnd: str
        :type out_over: str

        :return: addition result.
        :rtype: FixNum"""

        return self._op_out_casting(self.__add__, *args, **kwargs)

    # ## Subtraction methods
    def __sub__(self, other):
        tmp_val = self.value - other.value
        tmp_fmt = FixFmt(self.fmt.signed or other.fmt.signed,
                         max(self.fmt.int_bits, other.fmt.int_bits)+1,
                         max(self.fmt.frac_bits, other.fmt.frac_bits))
        if (self.rnd != other.rnd) or (self.over != other.over):
            print('_WARNING_: operators have round and / or overflow methods ' +
                  'not equal, those of first operator will be considered')
        return FixNum(tmp_val, tmp_fmt, self.rnd, self.over)

    def sub(self, *args, **kwargs):
        """Subtraction method.

        *Usage: sub(other, out_fmt=None, out_rnd="SymZero", out_over="Wrap")*

        It allows to decide output format.
        If not indicated, full-precision format will be adopted.

        :param other: fix-point object.
        :param out_fmt: optional format operation result can be casted to.
        :param out_rnd: round method adopted on result (default ```SymZero```).
        :param out_over: overflow method adopted on result (default ```Wrap```).

        :type other: FixNum
        :type out_fmt: FixFmt
        :type out_rnd: str
        :type out_over: str

        :return: operation result.
        :rtype: FixNum"""

        return self._op_out_casting(self.__sub__, *args, **kwargs)

    # ## Multiplication methods
    def __mul__(self, other):
        tmp_val = self.value * other.value
        tmp_fmt = FixFmt(self.fmt.signed or other.fmt.signed,
                         self.fmt.int_bits + other.fmt.int_bits,
                         self.fmt.frac_bits + other.fmt.frac_bits)
        if (self.rnd != other.rnd) or (self.over != other.over):
            print('_WARNING_: operators have round and / or overflow methods ' +
                  'not equal, those of first operator will be considered')
        return FixNum(tmp_val, tmp_fmt, self.rnd, self.over)

    def mult(self, *args, **kwargs):
        """Multiplication method.

        *Usage: mult(other, out_fmt=None, out_rnd="SymZero", out_over="Wrap")*

        It allows to decide output format.
        If not indicated, full-precision format will be adopted.

        :param other: fix-point object.
        :param out_fmt: optional format operation result can be casted to.
        :param out_rnd: round method adopted on result (default ```SymZero```).
        :param out_over: overflow method adopted on result (default ```Wrap```).

        :type other: FixNum
        :type out_fmt: FixFmt
        :type out_rnd: str
        :type out_over: str

        :return: operation result.
        :rtype: FixNum"""

        return self._op_out_casting(self.__mul__, *args, **kwargs)

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


# private methods
def _bin2fixstring(value, out_length):
    """Convert a number to bin format with leading zeros."""

    value_bin_no_prefix = bin(value)[2:]

    return '0b' + (out_length - len(value_bin_no_prefix)) * '0' + value_bin_no_prefix
