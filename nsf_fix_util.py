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

    def __repr__(self):
        return "(" + str(self.signed) + "," \
           + str(self.intBits) + "," \
           + str(self.fracBits) + ")\n\n" \
           + "<nsf_fix_util.FixFmt at " + hex(id(self)) + '>'

    def bit_length(self):
        return int(self.signed) \
            + self.intBits \
            + self.fracBits

    def range(self):
        """Return the range representable by fix format object"""
        pass
