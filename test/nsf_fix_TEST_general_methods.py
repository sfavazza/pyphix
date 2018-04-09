import unittest as utst
import numpy as np
import importlib as imp

import nsf_fix as fi

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
        self.assertEqual(self.fmt.max, 2**self.fmt.int_bits - 2**(-self.fmt.frac_bits))
        # min
        self.assertEqual(self.fmt.min, -2**self.fmt.frac_bits)
        # range
        self.assertTrue(isinstance(self.fmt.range, tuple))
        self.assertEqual(self.fmt.range, (self.fmt.max, self.fmt.min))
        # tuple
        self.assertTrue(isinstance(self.fmt.tuple, tuple))
        # list
        self.assertTrue(isinstance(self.fmt.list, list))


class TestNsfFixNumMethods(utst.TestCase):

    def test_private_methods(self):
        pass

    def test_public_methods(self):
        pass

    def test_container_methods(self):
        pass

    def test_generator(self):
        pass

    def test_operators(self):
        pass

    def test_logic_operations(self):
        pass


if __name__ == '__main__':
    utst.main()
