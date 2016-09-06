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

    def range(self):
        """Return the range representable by fix format object"""
        pass
