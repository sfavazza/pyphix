import nsf_fix_util as fu
import numpy as np
from numpy import bitwise_and as np_and
from numpy import bitwise_not as np_not
# for decorator
import time


# function performance decorator
def time_perfomance(f):

    def function_exec_time_wrapper(*args, **kwargs):
        startTime = time.time()
        functionObject = f(*args, **kwargs)
        endTime = time.time()
        print("Time to run function " + f.__name__ + ": {}".format(endTime - startTime))
        return functionObject

    return function_exec_time_wrapper


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

    Saturation method
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
                 fmt: fu.FixFmt,
                 rnd="SymZero",
                 over="Wrap"):

        # init instance members
        self.fmt = fmt
        self.rnd = rnd
        self.over = over

        # cast to np if necessary
        if not isinstance(value, np.ndarray):
            value = np.array(value)

        # to integer representation coefficient
        toIntCoeff = 2**self.fmt.fracBits
        # turn input into 1D array (to allow iteration through out all values)
        self.shape = value.shape
        self.value = np.reshape(value, -1)*toIntCoeff

        self._fixSizeMask = (1 << self.fmt.bit_length())-1

        # round
        self._round()

        # check overflow
        self._over(toIntCoeff)
        # TODO: tackle with negative frac or int bits number in format
        self.value = np.reshape(self.value/toIntCoeff, self.shape)

    # private methods
    def _round(self):
        '''Perform specified rounding on input values'''
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
        '''Implement specified overflow method on input value'''
        if self.over == "Sat":
            self.value = np.maximum(
                np.minimum(self.value, self.fmt.max()*toIntCoeff),
                self.fmt.min()*toIntCoeff)
        elif self.over == "Wrap":
            # selection masks
            highBitMask = (1 << (self.fmt.bit_length()-1))
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

    # methods
    def change_fix(self,
                   newFmt: fu.FixFmt,
                   newRnd: str=None,
                   newOver: str=None):
        """Change fix parameters of current object.

        :param newFmt: new format (mandatory)
        :param newRnd: new round method, if not specified current is used
        :param newOver: new saturation method, if not specified current is used
        """
        return FixNum(self.value, newFmt,
                      self.rnd if newRnd is None else newRnd,
                      self.over if newOver is None else newOver)

    @property
    def bin(self):
        tmpVal = np.reshape(self.value, -1) * 2**self.fmt.fracBits
        tmpBin = np.array([bin(np.int(x)) if x >= 0 else
                           bin((~np.int(-x) + 1) & self._fixSizeMask) for x in tmpVal])
        return np.reshape(tmpBin, self.shape)

    @property
    def hex(self):
        return np.array([hex(x) for x in self.int])

    @property
    def int(self):
        tmpVal = np.reshape(self.value, -1) * 2**self.fmt.fracBits
        tmpBin = np.array([np.int(x) if x >= 0 else
                           (~np.int(-x) + 1) & self._fixSizeMask for x in tmpVal])
        return np.reshape(tmpBin, self.shape)

    @property
    def fimath(self):
        """Return fix math as tuple (round method, overflow mode).
        """
        return (self.rnd, self.over)

    def __str__(self):
        return """
        """ + str(self.value) + """
        format: """ + str(self.fmt) + """
        round: """ + self.rnd + """
        saturate: """ + self.over

    def __repr__(self):
        return """
        """ + str(self.value) + """
        format: """ + str(self.fmt) + """
        round: """ + self.rnd + """
        saturate: """ + self.over + """

        <nsf_fix.FixNum at """ + hex(id(self)) + '>'

    def __len__(self):
        return len(self.value)

    def __contains__(self, elem):
        if isinstance(elem, FixNum):
            return elem.value in self.value
        else:
            return elem in self.value

    # operators

    # ## Addition methods
    def __add__(self, other):
        tmpVal = self.value + other.value
        tmpFmt = fu.FixFmt(max(self.fmt.signed, other.fmt.signed),
                           max(self.fmt.intBits, other.fmt.intBits)+1,
                           max(self.fmt.fracBits, other.fmt.fracBits))
        if (self.rnd != other.rnd) or (self.over != other.over):
            print('_WARNING_: operators have round and/or overflow methods ' +
                  'not equal, those of first operator will be considered')
        return FixNum(tmpVal, tmpFmt, self.rnd, self.over)

    def add(self, other, outFmt=None, outRnd="SymZero", outOver="Wrap"):
        '''
        Addition method.
        It allows to decide output format.
        If not indicated, full-precision format will be adopted
        '''
        tmpVal = self.value + other.value
        tmpFmt = fu.FixFmt(max(self.fmt.signed, other.fmt.signed),
                           max(self.fmt.intBits, other.fmt.intBits)+1,
                           max(self.fmt.fracBits, other.fmt.fracBits)
                           ) if outFmt is None else outFmt
        return FixNum(tmpVal, tmpFmt, outRnd, outOver)

    # ## Subtraction methods
    def __sub__(self, other):
        tmpVal = self.value - other.value
        tmpFmt = fu.FixFmt(max(self.fmt.signed, other.fmt.signed),
                           max(self.fmt.intBits, other.fmt.intBits)+1,
                           max(self.fmt.fracBits, other.fmt.fracBits))
        if (self.rnd != other.rnd) or (self.over != other.over):
            print('_WARNING_: operators have round and / or overflow methods ' +
                  'not equal, those of first operator will be considered')
        return FixNum(tmpVal, tmpFmt, self.rnd, self.over)

    def sub(self, other, outFmt=None, outRnd="SymZero", outOver="Wrap"):
        '''
        Subtraction method.
        It allows to decide output format.
        If not indicated, full-precision format will be adopted
        '''
        tmpVal = self.value - other.value
        tmpFmt = fu.FixFmt(max(self.fmt.signed, other.fmt.signed),
                           max(self.fmt.intBits, other.fmt.intBits)+1,
                           max(self.fmt.fracBits, other.fmt.fracBits)
                           ) if outFmt is None else outFmt
        return FixNum(tmpVal, tmpFmt, outRnd, outOver)

    # ## Multiplication methods
    def __mul__(self, other):
        tmpVal = self.value * other.value
        tmpSign = max(self.fmt.signed, other.fmt.signed)
        tmpFmt = fu.FixFmt(tmpSign,
                           self.fmt.intBits + other.fmt.intBits + 1 if
                           tmpSign else self.fmt.intBits + other.fmt.intBits,
                           self.fmt.fracBits + other.fmt.fracBits)
        if (self.rnd != other.rnd) or (self.over != other.over):
            print('_WARNING_: operators have round and / or overflow methods ' +
                  'not equal, those of first operator will be considered')
        return FixNum(tmpVal, tmpFmt, self.rnd, self.over)

    def mult(self, other, outFmt=None, outRnd="SymZero", outOver="Wrap"):
        '''
        Multiplication method.
        It allows to decide output format.
        If not indicated, full-precision format will be adopted
        '''
        tmpVal = self.value * other.value
        tmpSign = max(self.fmt.signed, other.fmt.signed)
        tmpFmt = fu.FixFmt(tmpSign,
                           self.fmt.intBits + other.fmt.intBits + 1 if
                           tmpSign else self.fmt.intBits + other.fmt.intBits,
                           self.fmt.fracBits + other.fmt.fracBits
                           ) if outFmt is None else outFmt
        return FixNum(tmpVal, tmpFmt, outRnd, outOver)

    # ## Negation method
    def __neg__(self):
        return FixNum(-self.value, self.fmt, self.rnd, self.over)
