class FixFmt:
    """Fix format class
    """

    def __init__(self,
                 signed: bool,
                 intBits,
                 fracBits):
        self.signed = signed
        self.intBits = intBits
        self.fracBits = fracBits

    def __str__(self):
        return "(" + str(self.signed) + "," \
           + str(self.intBits) + "," \
           + str(self.fracBits) + ")"

    # def signed(self):
    #     return self._signed

    # def intBits(self):
    #     return self._intBits

    # def fracBits(self):
    #     return self._fracBits

    def bit_length(self):
        return int(self._signed) \
            + self.intBits \
            + self.fracBits

    def range(self):
        """Return the range representable by fix format object"""
        pass
