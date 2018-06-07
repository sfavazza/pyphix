"""Test FixNum features."""

__author__ = "Samuele FAVAZZA"
__copyright__ = "Copyright 2018, Samuele FAVAZZA"

import unittest as utst
import importlib as imp

import numpy as np

from pyphix import fix as fi

# reload module to be sure last changes are taken into account
imp.reload(fi)


class TestFixRoundOverMethods(utst.TestCase):
    """Test FixNum features."""

    # define formats
    s_4 = fi.FixFmt(True, 0, 4)
    u_4 = fi.FixFmt(False, 0, 4)

    def test_known_signed_round(self):
        """Test round methods on signed values."""

        # create test vector
        to_int_coeff = 2**self.s_4.frac_bits
        tst_pattern_signed = np.array([2.6, 2.5, 2.4, 1.7, 1.5, 1.2,
                                       -4.3, -4.5, -4.8, -5.4, -5.5, -5.6]) / to_int_coeff
        # expected values
        tst_exp_signed = {}
        tst_exp_signed['SymInf'] = np.array([3, 3, 2, 2, 2, 1,
                                             -4, -5, -5, -5, -6, -6]) / to_int_coeff
        tst_exp_signed['SymZero'] = np.array([3, 2, 2, 2, 1, 1,
                                              -4, -4, -5, -5, -5, -6]) / to_int_coeff
        tst_exp_signed['NonSymPos'] = np.array([3, 3, 2, 2, 2, 1,
                                                -4, -4, -5, -5, -5, -6]) / to_int_coeff
        tst_exp_signed['NonSymNeg'] = np.array([3, 2, 2, 2, 1, 1,
                                                -4, -5, -5, -5, -6, -6]) / to_int_coeff
        tst_exp_signed['ConvEven'] = np.array([3, 2, 2, 2, 2, 1,
                                               -4, -4, -5, -5, -6, -6]) / to_int_coeff
        tst_exp_signed['ConvOdd'] = np.array([3, 3, 2, 2, 1, 1,
                                              -4, -5, -5, -5, -5, -6]) / to_int_coeff
        tst_exp_signed['Floor'] = np.array([2, 2, 2, 1, 1, 1,
                                            -5, -5, -5, -6, -6, -6]) / to_int_coeff
        tst_exp_signed['Ceil'] = np.array([3, 3, 3, 2, 2, 2,
                                           -4, -4, -4, -5, -5, -5]) / to_int_coeff

        # apply round methods on test pattern
        tst_fix_signed = {key: fi.FixNum(tst_pattern_signed,
                                         self.s_4,
                                         key,
                                         'Wrap')
                          for key in tst_exp_signed}
        # verify
        for key in tst_exp_signed:
            np.testing.assert_array_equal(tst_exp_signed[key],
                                          tst_fix_signed[key].value)

    def test_known_unsigned_round(self):
        """Test round methods on unsigned values."""

        # create test vector
        to_int_coeff = 2**self.s_4.frac_bits
        tst_pattern_unsigned = np.array([2.6, 2.5, 2.4, 1.7, 1.5, 1.2,
                                         4.3, 4.5, 4.8, 5.4, 5.5, 5.6]) / to_int_coeff

        # expected values
        tst_exp_unsigned = {}
        tst_exp_unsigned['SymInf'] = np.array([3, 3, 2, 2, 2, 1,
                                               4, 5, 5, 5, 6, 6]) / to_int_coeff
        tst_exp_unsigned['SymZero'] = np.array([3, 2, 2, 2, 1, 1,
                                                4, 4, 5, 5, 5, 6]) / to_int_coeff
        tst_exp_unsigned['NonSymPos'] = np.array([3, 3, 2, 2, 2, 1,
                                                  4, 5, 5, 5, 6, 6]) / to_int_coeff
        tst_exp_unsigned['NonSymNeg'] = np.array([3, 2, 2, 2, 1, 1,
                                                  4, 4, 5, 5, 5, 6]) / to_int_coeff
        tst_exp_unsigned['ConvEven'] = np.array([3, 2, 2, 2, 2, 1,
                                                 4, 4, 5, 5, 6, 6]) / to_int_coeff
        tst_exp_unsigned['ConvOdd'] = np.array([3, 3, 2, 2, 1, 1,
                                                4, 5, 5, 5, 5, 6]) / to_int_coeff
        tst_exp_unsigned['Floor'] = np.array([2, 2, 2, 1, 1, 1,
                                              4, 4, 4, 5, 5, 5]) / to_int_coeff
        tst_exp_unsigned['Ceil'] = np.array([3, 3, 3, 2, 2, 2,
                                             5, 5, 5, 6, 6, 6]) / to_int_coeff

        # apply round methods on test pattern
        tst_fix_unsigned = {key: fi.FixNum(tst_pattern_unsigned,
                                           self.u_4,
                                           key,
                                           'Wrap')
                            for key in tst_exp_unsigned}
        # verify
        for key in tst_exp_unsigned:
            np.testing.assert_array_equal(tst_exp_unsigned[key],
                                          tst_fix_unsigned[key].value)

    def test_known_signed_overflow(self):
        """Test overflow methods on signed values."""

        # saturation overflow
        # max 0.9375 min -1
        over_pattern_signed = np.array([1, 2, 3.0001, 1-2**(-4),
                                        1-2**(-5), 1-2**(-3), -1, -1-2**(-4)])
        over_exp_signed = {}
        over_exp_signed['Sat'] = np.array([.9375, .9375, .9375, .9375, .9375, .875,
                                           -1, -1])
        # wrap overflow
        over_exp_signed['Wrap'] = np.array([-1, 0, -1, .9375, .9375, .875,
                                            -1, .9375])

        # apply overflow methods
        over_fix_signed = {key: fi.FixNum(over_pattern_signed,
                                          self.s_4,
                                          'SymZero',
                                          key)
                           for key in over_exp_signed}
        # verify
        for key in over_exp_signed:
            np.testing.assert_array_equal(over_exp_signed[key],
                                          over_fix_signed[key].value)

    def test_known_unsigned_overflow(self):
        """Test overflow methods on unsigned values."""

        # saturation overflow
        # max 0.9375 min 0
        over_pattern_unsigned = np.array([1, 2, 3.0001, 1-2**(-4),
                                          1-2**(-5), 1-2**(-3), -1, -1-2**(-4)])
        over_exp_unsigned = {}
        over_exp_unsigned['Sat'] = np.array([.9375, .9375, .9375, .9375, .9375, .875,
                                             0, 0])

        # wrap overflow
        over_exp_unsigned['Wrap'] = np.array([0, 0, 0, .9375, .9375, .875,
                                              0, .9375])

        # apply overflow methods
        over_fix_unsigned = {key: fi.FixNum(over_pattern_unsigned,
                                            self.u_4,
                                            'SymZero',
                                            key)
                             for key in over_exp_unsigned}
        # verify
        for key in over_exp_unsigned:
            np.testing.assert_array_equal(over_exp_unsigned[key],
                                          over_fix_unsigned[key].value)

    @staticmethod
    def test_change_fix():
        """Test fimath change."""

        # create simple vector
        s2_5 = fi.FixFmt(True, 2, 5)
        u1_3 = fi.FixFmt(False, 1, 3)

        input_vec = [-3.56344, 0, 99999, -1.8]
        input_fix_vec = [-3.5625, 0, -1, -1.8125]
        output_fix_vec = [0.375, 0, 1, .125]
        fix_under_test = fi.FixNum(input_vec, s2_5, 'SymZero')

        np.testing.assert_array_equal(input_fix_vec, fix_under_test.value)
        np.testing.assert_array_equal(output_fix_vec, fix_under_test.change_fix(u1_3, 'NonSymNeg').value)


class TestFixNumMethods(utst.TestCase):
    """Test FixNum class general methods."""

    # define commons
    s3_7 = fi.FixFmt(True, 3, 7)

    def test_public_methods(self):
        """Test FixNum representations."""

        # general vectors
        src_vec = [.0078125, 7.724, -3.72455, -7, 0, -8]
        src_fix_vec = fi.FixNum(src_vec, self.s3_7)

        # bin
        exp_bin_vec = ['0b00000000001', '0b01111011101', '0b11000100011',
                       '0b10010000000', '0b00000000000', '0b10000000000']
        np.testing.assert_array_equal(src_fix_vec.binfmt, exp_bin_vec)

        # hex
        exp_hex_vec = ['0x001', '0x3dd', '0x623', '0x480', '0x000', '0x400']
        np.testing.assert_array_equal(src_fix_vec.hexfmt, exp_hex_vec)

        # int
        exp_int_vec = [1, 989, 1571, 1152, 0, 1024]
        np.testing.assert_array_equal(src_fix_vec.intfmt, exp_int_vec)

    def test_container_methods(self):
        """Test FixNum container behavior."""

        # random vector
        random_vec = np.array([[0.3046875, 0.8515625, 0.4609375, 0.0703125],
                               [0.8359375, 0.8125, 0.8046875, 0.796875]])

        # test fix vector
        test_fix_vec = fi.FixNum(random_vec, self.s3_7)

        # contains
        self.assertTrue(0.8125 in test_fix_vec)  # value
        self.assertTrue(fi.FixNum(0.8125, self.s3_7) in test_fix_vec)  # fix
        self.assertFalse(-70 in test_fix_vec)  # value
        self.assertFalse(fi.FixNum(-70, self.s3_7) in test_fix_vec)  # fix

        # get item
        self.assertTrue(isinstance(test_fix_vec[0][3], fi.FixNum))
        self.assertEqual(test_fix_vec[-1][-1], fi.FixNum(.796875, self.s3_7))

        # set item
        test_fix_vec[0, 1] = 2     # in fmt range
        random_vec[0, 1] = 2
        test_fix_vec[1, 1] = 1000  # out of fmt range
        random_vec[1, 1] = 1000

        self.assertEqual(test_fix_vec[0, 1], fi.FixNum(2, self.s3_7))
        self.assertEqual(test_fix_vec[1, 1], fi.FixNum(1000, self.s3_7))
        np.testing.assert_array_equal(test_fix_vec.value, fi.FixNum(random_vec, self.s3_7).value)

    def test_generator(self):
        """Test FixNum generator feature."""

        pass

    def test_operators(self):
        """Test FixNum supported operations."""

        pass

    def test_logic_operations(self):
        """Test FixNum logic operations."""

        pass


if __name__ == '__main__':
    utst.main()
