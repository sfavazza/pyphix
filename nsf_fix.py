class rndType(enumerate):
    """Round type class.

    Define common numbers round methods.

    """
    # Raw truncation
    Trunc = 1
    # Positive numbers tend to inf, negative ones to -inf
    SymInf = 2
    # Numbers tend toward zero
    SymZero = 3
    # Positive and negat
    NonSymPos = 4
    NonSymNeg = 5
    ConvEven = 6
    ConvOdd = 7
    Floor = 8
    Ceil = 9


class satType(enumerate):

    Sat = 1
    Wrap = 2


class NsfFix:
    """Class definition
    """

    def __init__(self,
                 value,
                 fixFmt,
                 rndMode: rndType = 'NonSymPos',
                 satMode: satType = 'Sat'):
        self._value = value
        self._fixFmt = fixFmt
        self._rndMode = rndMode
        self._satMode = satMode

    # methods
    def get_fmt(self):
        return self._fixFmt

    # operators
    def __add__(self, other):
        pass

