from enum import Enum


class rndType(Enum):
    """Round type class.

    Define common numbers round methods.
    SymInf    : positive numbers tends to +inf, negative numbers to -inf
    SymZero   : round toward zero
    NonSymPos : round toward +inf
    NonSymNeg : round toward -inf
    ConvEven  : round to closest even
    ConvOdd   : round to closest odd
    Floor     : round to largest previous
    Ceil      : round to smallest following
    """
    SymInf = 1
    SymZero = 2
    NonSymPos = 3
    NonSymNeg = 4
    ConvEven = 5
    ConvOdd = 6
    Floor = 7
    Ceil = 8


class satType(Enum):
    """Saturation type class

    Define behavior in case of overflow.
    Sat  : saturate
    Wrap : wrap around
    """

    Sat = 1
    Wrap = 2


class FixFmt:
    """Fix format class
    """

    def __init__(self,
                 signed: bool,
                 intBits,
                 fracBits):
        self._signed = signed
        self._intBits = intBits
        self._fracBits = fracBits

    def __str__(self):
        return "(" + str(self._signed) + "," \
           + str(self._intBits) + "," \
           + str(self._fracBits) + ")"

    def bit_length(self):
        return int(self._signed) \
            + self._intBits \
            + self._fracBits
