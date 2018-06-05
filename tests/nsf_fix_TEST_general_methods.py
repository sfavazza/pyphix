import unittest as utst
import numpy as np
import importlib as imp

from pyphix import fix as fi

########################################################
# IMPORTANT: run this script from its parent directory #
########################################################

# reload module to be sure last changes are taken into account
imp.reload(fi)


class TestNsfFixFmtMethods(utst.TestCase):

    # define fmt object under test
    fmt = fi.FixFmt(True, 21, 4)

    def test_properties(self):
        # bit nuber
        self.assertEqual(self.fmt.bit_length,
                         self.fmt.int_bits + self.fmt.frac_bits + int(self.fmt.signed))
        # max
        exp_max = 2**self.fmt.int_bits - 2**(-self.fmt.frac_bits)
        self.assertEqual(self.fmt.maxvalue, exp_max)
        # min
        exp_min = -2**self.fmt.int_bits
        self.assertEqual(self.fmt.minvalue, exp_min)
        # range
        self.assertTrue(isinstance(self.fmt.range, tuple))
        self.assertEqual(self.fmt.range, (exp_min, exp_max))
        # tuple
        self.assertTrue(isinstance(self.fmt.tuplefmt, tuple))
        # list
        self.assertTrue(isinstance(self.fmt.listfmt, list))


class TestNsfFixNumMethods(utst.TestCase):

    # define commons
    s3_7 = fi.FixFmt(True, 3, 7)

    def test_public_methods(self):
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
        pass

    def test_operators(self):
        pass

    def test_logic_operations(self):
        pass


if __name__ == '__main__':
    utst.main()
