import nsf_fix_util as fu


class FixNum:
    """Fixed point number class

    :param value: value to represent in fix point
    :type value: float
    :param fmt: fix point format
    :type fmt: FixFmt
    :return: fixed point object
    :rtype: NsfFix
    """

    def __init__(self,
                 value,
                 fmt: fu.FixFmt,
                 rnd=fu.rndType.NonSymPos,
                 sat=fu.satType.Sat):
        self._value = value  # todo: should be directly converted
        self._fmt = fmt
        self._rnd = rnd
        self._sat = sat

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
