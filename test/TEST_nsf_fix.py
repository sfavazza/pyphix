import unittest as utst
import numpy as np
import importlib as imp

import nsf_fix as fi
import nsf_fix_util as fu

########################################################
# IMPORTANT: run this script from its parent directory #
########################################################

# reload module to be sure last changes are taken into account
imp.reload(fu)
imp.reload(fi)


class TestNsfFixKnownValues(utst.TestCase):

    # ******************************
    # TEST ROUND METHODS - SIGNED
    # ******************************

    # define format
    s_4 = fu.FixFmt(True, 0, 4)
    # create test vector
    realCoeff = 2**s_4.fracBits
    tstPatternSigned = np.array([2.6, 2.5, 2.4, 1.7, 1.5, 1.2,
                                 -4.3, -4.5, -4.8, -5.4, -5.5, -5.6]) / \
        realCoeff
    # expected values
    tstExpSigned = {}
    tstExpSigned['SymInf'] = np.array([3, 3, 2, 2, 2, 1,
                                       -4, -5, -5, -5, -6, -6]) / realCoeff
    tstExpSigned['SymZero'] = np.array([3, 2, 2, 2, 1, 1,
                                        -4, -4, -5, -5, -5, -6]) / realCoeff
    tstExpSigned['NonSymPos'] = np.array([3, 3, 2, 2, 2, 1,
                                          -4, -4, -5, -5, -5, -6]) / realCoeff
    tstExpSigned['NonSymNeg'] = np.array([3, 2, 2, 2, 1, 1,
                                          -4, -5, -5, -5, -6, -6]) / realCoeff
    tstExpSigned['ConvEven'] = np.array([3, 2, 2, 2, 2, 1,
                                         -4, -4, -5, -5, -6, -6]) / realCoeff
    tstExpSigned['ConvOdd'] = np.array([3, 3, 2, 2, 1, 1,
                                        -4, -5, -5, -5, -5, -6]) / realCoeff
    tstExpSigned['Floor'] = np.array([2, 2, 2, 1, 1, 1,
                                      -5, -5, -5, -6, -6, -6]) / realCoeff
    tstExpSigned['Ceil'] = np.array([3, 3, 3, 2, 2, 2,
                                     -4, -4, -4, -5, -5, -5]) / realCoeff

    # ## Compare against known values
    def test_NsfFix_KnownSignedValues(self):
        # apply round methods on test pattern
        tstFixSigned = {key: fi.FixNum(self.tstPatternSigned,
                                       self.s_4,
                                       key,
                                       'Wrap')
                        for key in self.tstExpSigned.keys()}
        # verify
        for key in self.tstExpSigned.keys():
            np.testing.assert_array_equal(self.tstExpSigned[key],
                                          tstFixSigned[key].value)

    # ******************************
    # TEST ROUND METHODS - UNSIGNED
    # ******************************
    # define format
    u_4 = fu.FixFmt(False, 0, 4)
    # create test vector
    realCoeff = 2**s_4.fracBits
    tstPatternUnsigned = np.array([2.6, 2.5, 2.4, 1.7, 1.5, 1.2,
                                   4.3,  4.5,  4.8,  5.4,  5.5,  5.6]) / \
        realCoeff

    # expected values
    tstExpUnsigned = {}
    tstExpUnsigned['SymInf'] = np.array([3, 3, 2, 2, 2, 1,
                                         4, 5, 5, 5, 6, 6]) / realCoeff
    tstExpUnsigned['SymZero'] = np.array([3, 2, 2, 2, 1, 1,
                                          4, 4, 5, 5, 5, 6]) / realCoeff
    tstExpUnsigned['NonSymPos'] = np.array([3, 3, 2, 2, 2, 1,
                                            4, 5, 5, 5, 6, 6]) / realCoeff
    tstExpUnsigned['NonSymNeg'] = np.array([3, 2, 2, 2, 1, 1,
                                            4, 4, 5, 5, 5, 6]) / realCoeff
    tstExpUnsigned['ConvEven'] = np.array([3, 2, 2, 2, 2, 1,
                                           4, 4, 5, 5, 6, 6]) / realCoeff
    tstExpUnsigned['ConvOdd'] = np.array([3, 3, 2, 2, 1, 1,
                                          4, 5, 5, 5, 5, 6]) / realCoeff
    tstExpUnsigned['Floor'] = np.array([2, 2, 2, 1, 1, 1,
                                        4, 4, 4, 5, 5, 5]) / realCoeff
    tstExpUnsigned['Ceil'] = np.array([3, 3, 3, 2, 2, 2,
                                       5, 5, 5, 6, 6, 6]) / realCoeff

    def test_NsfFix_KnownUnsignedValues(self):
        # apply round methods on test pattern
        tstFixUnsigned = {key: fi.FixNum(self.tstPatternUnsigned,
                                         self.u_4,
                                         key,
                                         'Wrap')
                          for key in self.tstExpUnsigned.keys()}
        # verify
        for key in self.tstExpUnsigned.keys():
            np.testing.assert_array_equal(self.tstExpUnsigned[key],
                                          tstFixUnsigned[key].value)

    # ******************************
    # TEST OVERFLOW METHODS - SIGNED
    # ******************************
    # saturation overflow
    # max 0.9375 min -1
    overPatternSigned = np.array([1, 2, 3.0001, 1-2**(-4),
                                  1-2**(-5), 1-2**(-3), -1, -1-2**(-4)])
    overExpSigned = {}
    overExpSigned['Sat'] = np.array([.9375, .9375, .9375, .9375, .9375, .875,
                                     -1, -1])
    # wrap overflow
    overExpSigned['Wrap'] = np.array([-1, 0, -1, .9375, .9375, .875,
                                      -1, .9375])

    def test_NsfFix_KnownSignedOverflow(self):
        # apply overflow methods
        overFixSigned = {key: fi.FixNum(self.overPatternSigned,
                                        self.s_4,
                                        'SymZero',
                                        key)
                         for key in self.overExpSigned.keys()}
        # verify
        for key in self.overExpSigned.keys():
            np.testing.assert_array_equal(self.overExpSigned[key],
                                          overFixSigned[key].value)

    # ******************************
    # TEST OVERFLOW METHODS - UNSIGNED
    # ******************************
    # saturation overflow
    # max 0.9375 min 0
    overPatternUnsigned = np.array([1, 2, 3.0001, 1-2**(-4),
                                    1-2**(-5), 1-2**(-3), -1, -1-2**(-4)])
    overExpUnsigned = {}
    overExpUnsigned['Sat'] = np.array([.9375, .9375, .9375, .9375, .9375, .875,
                                       0, 0])

    # wrap overflow
    overExpUnsigned['Wrap'] = np.array([0, 0, 0, .9375, .9375, .875,
                                        0, .9375])

    def test_NsfFix_KnownUnsignedOverflow(self):
        # apply overflow methods
        overFixUnsigned = {key: fi.FixNum(self.overPatternUnsigned,
                                          self.u_4,
                                          'SymZero',
                                          key)
                           for key in self.overExpUnsigned.keys()}
        # verify
        for key in self.overExpUnsigned.keys():
            np.testing.assert_array_equal(self.overExpUnsigned[key],
                                          overFixUnsigned[key].value)

if __name__ == '__main__':
    utst.main()
