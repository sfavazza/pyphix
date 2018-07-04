"""Test FixNum features."""

__author__ = "Samuele FAVAZZA"
__copyright__ = "Copyright 2018, Samuele FAVAZZA"

import unittest as utst
import importlib as imp

import numpy as np
from numpy import bitwise_and as np_and

from pyphix import fix

# reload module to be sure last changes are taken into account
imp.reload(fix)


class TestFixRoundOverMethods(utst.TestCase):
    """Test FixNum features."""

    # define formats
    s_4 = fix.FixFmt(True, 0, 4)
    u_4 = fix.FixFmt(False, 0, 4)

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
        tst_fix_signed = {key: fix.FixNum(tst_pattern_signed,
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
        tst_fix_unsigned = {key: fix.FixNum(tst_pattern_unsigned,
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
        over_fix_signed = {key: fix.FixNum(over_pattern_signed,
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
        over_fix_unsigned = {key: fix.FixNum(over_pattern_unsigned,
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
        s2_5 = fix.FixFmt(True, 2, 5)
        u1_3 = fix.FixFmt(False, 1, 3)

        input_vec = [-3.56344, 0, 99999, -1.8]
        input_fix_vec = [-3.5625, 0, -1, -1.8125]
        output_fix_vec = [0.375, 0, 1, .125]
        fix_under_test = fix.FixNum(input_vec, s2_5, 'SymZero')

        np.testing.assert_array_equal(input_fix_vec, fix_under_test.value)
        np.testing.assert_array_equal(output_fix_vec, fix_under_test.change_fix(u1_3, 'NonSymNeg').value)


class TestFixNumMethods(utst.TestCase):
    """Test FixNum class general methods."""

    # define commons
    s3_7 = fix.FixFmt(True, 3, 7)

    def test_public_methods(self):
        """Test FixNum representations."""

        # general vectors
        src_vec = [.0078125, 7.724, -3.72455, -7, 0, -8]
        src_fix_vec = fix.FixNum(src_vec, self.s3_7)

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
        test_fix_vec = fix.FixNum(random_vec, self.s3_7)

        # contains
        self.assertTrue(0.8125 in test_fix_vec)  # value
        self.assertTrue(fix.FixNum(0.8125, self.s3_7) in test_fix_vec)  # fix
        self.assertFalse(-70 in test_fix_vec)  # value
        self.assertFalse(fix.FixNum(-70, self.s3_7) in test_fix_vec)  # fix

        # get item
        self.assertTrue(isinstance(test_fix_vec[0][3], fix.FixNum))
        self.assertEqual(test_fix_vec[-1][-1], fix.FixNum(.796875, self.s3_7))

        # set item
        test_fix_vec[0, 1] = 2     # in fmt range
        random_vec[0, 1] = 2
        test_fix_vec[1, 1] = 1000  # out of fmt range
        random_vec[1, 1] = 1000

        self.assertEqual(test_fix_vec[0, 1], fix.FixNum(2, self.s3_7))
        self.assertEqual(test_fix_vec[1, 1], fix.FixNum(1000, self.s3_7))
        np.testing.assert_array_equal(test_fix_vec.value, fix.FixNum(random_vec, self.s3_7).value)

    def test_generator(self):
        """Test FixNum generator feature."""

        # generate test data
        test_data = np.linspace(-16, 15, 100)

        # convert to fix-point object
        fmt = fix.FixFmt(True, 4, 12)
        test_fix = fix.FixNum(test_data, fmt, 'Ceil', over='Sat')

        # try to iterate through test object
        for idx, fix_element in enumerate(test_fix):
            self.assertEqual(fix_element, test_fix[idx])

    @staticmethod
    def test_addsub():
        """Test FixNum addition and subtraction operations."""

        # create formats
        fmt_a = fix.FixFmt(True, 2, 7)
        fmt_b = fix.FixFmt(False, 5, 2)

        # *** create intger version of operators A and B
        # max/min combination
        test_a_int = [fmt_a.maxvalue('int'), fmt_a.maxvalue('int'),
                      fmt_a.minvalue('int'), fmt_a.minvalue('int')]
        test_b_int = [fmt_b.maxvalue('int'), fmt_b.minvalue('int'),
                      fmt_b.maxvalue('int'), fmt_b.minvalue('int')]
        # add random data
        rand_generator = np.random.RandomState(122)       # make tests repeatible
        # NOTE: min and max are inverted as the negative minimum in 2's complement
        # is a positive greater than the maximum
        test_a_int = np.append(test_a_int, rand_generator.randint(fmt_a.minvalue('int'),
                                                                  fmt_a.maxvalue('int'), 100))
        test_b_int = np.append(test_b_int, rand_generator.randint(fmt_b.minvalue('int'),
                                                                  fmt_b.maxvalue('int'), 100))

        # create fixed test objects
        test_a_fix = fix.FixNum(test_a_int/2**fmt_a.frac_bits, fmt_a, "ConvEven", "Wrap")
        test_b_fix = fix.FixNum(test_b_int/2**fmt_b.frac_bits, fmt_b, "ConvEven", "Wrap")

        # **
        # *** ADDITION test
        # **
        # create result formats
        fmt_addsub_full = fix.FixFmt(fmt_a.signed or fmt_b.signed,
                                     max(fmt_a.int_bits, fmt_b.int_bits) + 1,
                                     max(fmt_a.frac_bits, fmt_b.frac_bits))
        fmt_addsub_small = fix.FixFmt(False, fmt_addsub_full.int_bits - 1, fmt_addsub_full.frac_bits - 1)
        fmt_addsub_big = fix.FixFmt(True, fmt_addsub_full.int_bits + 1, fmt_addsub_full.frac_bits + 1)

        # NOTE: before to perform the additions, the numbers must have the same fractional part length
        # the sign extension on the integer part comes for free, as in python 3 the integers uses an
        # 'infinite' numbers of bits (source: https://wiki.python.org/moin/BitwiseOperators)
        # create integer expected results for addition and subtraction
        int_addsub_aligned = [
            test_a_int + (test_b_int << abs(fmt_a.frac_bits - fmt_b.frac_bits)),  # b is always >= 0
            test_a_int - (test_b_int << abs(fmt_a.frac_bits - fmt_b.frac_bits))]

        # *** create expected results
        # prepare function list
        func_addsub = [test_a_fix.add, test_a_fix.sub]
        for idx, exp_int in enumerate(int_addsub_aligned):
            # * full precision (use mask to use wrap overflow method and remove the minus sign)
            exp_addsub_full_int = np_and(int_addsub_aligned[idx], fmt_addsub_full.mask)

            # * small format (perform saturation, no mask needed as the final format is unsigned)
            exp_addsub_small_int = int_addsub_aligned[idx] >> 1
            exp_addsub_small_int[exp_addsub_small_int >= fmt_addsub_small.maxvalue('int')] = \
                fmt_addsub_small.maxvalue('int')
            exp_addsub_small_int[exp_addsub_small_int <= fmt_addsub_small.minvalue('int')] = \
                fmt_addsub_small.minvalue('int')
            # * big format (no saturation needed)
            exp_addsub_big_int = np_and(int_addsub_aligned[idx] << 1, fmt_addsub_big.mask)

            # verify (compare integer version for simplicity)
            np.testing.assert_array_equal(func_addsub[idx](test_b_fix).intfmt, exp_addsub_full_int,
                                          err_msg='[FULL] Wrong addition result')
            np.testing.assert_array_equal(func_addsub[idx](test_b_fix, out_fmt=fmt_addsub_small,
                                                           out_rnd="NonSymNeg", out_over="Sat").intfmt,
                                          exp_addsub_small_int,
                                          err_msg='[SMALL] Wrong addition result')
            np.testing.assert_array_equal(func_addsub[idx](test_b_fix, out_fmt=fmt_addsub_big,
                                                           out_rnd="NonSymNeg", out_over="Sat").intfmt,
                                          exp_addsub_big_int,
                                          err_msg='[BIG] Wrong addition result')

    def test_mult(self):
        """Test FixNum multiplication operation."""

        pass

    def test_logic_operations(self):
        """Test FixNum logic operations."""

        pass


if __name__ == '__main__':
    utst.main()
