import unittest as utst
import numpy as np
import importlib as imp

from pyphix import fix as fi

########################################################
# IMPORTANT: run this script from its parent directory #
########################################################

# reload module to be sure last changes are taken into account
imp.reload(fi)


class TestNsfFixKnownValues(utst.TestCase):

    # define formats
    s_4 = fi.FixFmt(True, 0, 4)
    u_4 = fi.FixFmt(False, 0, 4)

    # ******************************
    # TEST ROUND METHODS - SIGNED
    # ******************************
    # ## Compare against known values
    def test_known_signed_values(self):

        # create test vector
        realCoeff = 2**self.s_4.frac_bits
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

        # apply round methods on test pattern
        tstFixSigned = {key: fi.FixNum(tstPatternSigned,
                                       self.s_4,
                                       key,
                                       'Wrap')
                        for key in tstExpSigned.keys()}
        # verify
        for key in tstExpSigned.keys():
            np.testing.assert_array_equal(tstExpSigned[key],
                                          tstFixSigned[key].value)

    # ******************************
    # TEST ROUND METHODS - UNSIGNED
    # ******************************
    def test_known_unsigned_values(self):

        # create test vector
        realCoeff = 2**self.s_4.frac_bits
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

        # apply round methods on test pattern
        tstFixUnsigned = {key: fi.FixNum(tstPatternUnsigned,
                                         self.u_4,
                                         key,
                                         'Wrap')
                          for key in tstExpUnsigned.keys()}
        # verify
        for key in tstExpUnsigned.keys():
            np.testing.assert_array_equal(tstExpUnsigned[key],
                                          tstFixUnsigned[key].value)

    # ******************************
    # TEST OVERFLOW METHODS - SIGNED
    # ******************************
    def test_known_signed_overflow(self):

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

        # apply overflow methods
        overFixSigned = {key: fi.FixNum(overPatternSigned,
                                        self.s_4,
                                        'SymZero',
                                        key)
                         for key in overExpSigned.keys()}
        # verify
        for key in overExpSigned.keys():
            np.testing.assert_array_equal(overExpSigned[key],
                                          overFixSigned[key].value)

    # ******************************
    # TEST OVERFLOW METHODS - UNSIGNED
    # ******************************
    def test_known_unsigned_overflow(self):

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

        # apply overflow methods
        overFixUnsigned = {key: fi.FixNum(overPatternUnsigned,
                                          self.u_4,
                                          'SymZero',
                                          key)
                           for key in overExpUnsigned.keys()}
        # verify
        for key in overExpUnsigned.keys():
            np.testing.assert_array_equal(overExpUnsigned[key],
                                          overFixUnsigned[key].value)

    # ******************************
    # TEST CHANGE FIX METHOD
    # ******************************
    def test_change_fix(self):

        # create simple vector
        s2_5 = fi.FixFmt(True, 2, 5)
        u1_3 = fi.FixFmt(False, 1, 3)

        input_vec = [-3.56344, 0, 99999, -1.8]
        input_fix_vec = [-3.5625, 0, -1, -1.8125]
        output_fix_vec = [0.375, 0, 1, .125]
        fix_under_test = fi.FixNum(input_vec, s2_5, 'SymZero')

        np.testing.assert_array_equal(input_fix_vec, fix_under_test.value)
        np.testing.assert_array_equal(output_fix_vec, fix_under_test.change_fix(u1_3, 'NonSymNeg').value)


if __name__ == '__main__':
    utst.main()
