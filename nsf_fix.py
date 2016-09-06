import nsf_fix_util as fu


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

        if rnd == "SymInf":
            pass
        elif rnd == "SymZero":
            pass
        elif rnd == "NonSymPos":
            pass
        elif rnd == "NonSymNeg":
            pass
        elif rnd == "ConvEven":
            pass
        elif rnd == "ConvOdd":
            pass
        elif rnd == "Floor":
            pass
        elif rnd == "Ceil":
            pass

        self._value = value  # todo: should be directly converted
        self._fmt = fmt
        self._rnd = rnd
        self._sat = over

    # methods
    def __str__(self):
        return """
        """ + str(self._value) + """
        format: """ + str(self._fmt) + """
        round: """ + self._rnd.name + """
        saturate: """ + self._sat.name

    def get_fmt(self):
        return self._fmt

    # operators
    def __add__(self, other):
        pass
