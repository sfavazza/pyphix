"""Test FixFmt features."""

import unittest as utst
import importlib as imp

from pyphix import fix

# reload module to be sure last changes are taken into account
imp.reload(fix)


class TestFixFmtMethods(utst.TestCase):
    """Test FixFmt features."""

    # define fmt object under test
    CONVERT_TO_INT = 4
    fmt = fix.FixFmt(True, 21, CONVERT_TO_INT)

    def test_bit_length(self):
        """DESCR: Test bit length."""

        # bit number
        self.assertEqual(self.fmt.bit_length,
                         self.fmt.int_bits + self.fmt.frac_bits + int(self.fmt.signed))

    def test_minmax(self):
        """DESCR: Test min max and range."""

        # max
        exp_max_float = 2**self.fmt.int_bits - 2**(-self.fmt.frac_bits)
        exp_max_int = int(exp_max_float*2**self.CONVERT_TO_INT)
        exp_max_hex = hex(exp_max_int & self.fmt.mask)
        exp_max_bin = bin(exp_max_int & self.fmt.mask)
        # correct bin representation with leading zeros
        exp_max_bin = '0b' + (self.fmt.bit_length - len(exp_max_bin[2:]))*'0' + exp_max_bin[2:]
        self.assertEqual(self.fmt.maxvalue(), exp_max_float)
        self.assertEqual(self.fmt.maxvalue(fix.EFormat.INT), exp_max_int)
        self.assertEqual(self.fmt.maxvalue(fix.EFormat.HEX), exp_max_hex)
        self.assertEqual(self.fmt.maxvalue(fix.EFormat.BIN), exp_max_bin)
        # min
        exp_min_float = -2**self.fmt.int_bits
        exp_min_int = int(exp_min_float*2**self.CONVERT_TO_INT)
        exp_min_hex = hex(exp_min_int & self.fmt.mask)
        exp_min_bin = bin(exp_min_int & self.fmt.mask)
        self.assertEqual(self.fmt.minvalue(), exp_min_float)
        self.assertEqual(self.fmt.minvalue(fix.EFormat.INT), exp_min_int)
        self.assertEqual(self.fmt.minvalue(fix.EFormat.HEX), exp_min_hex)
        self.assertEqual(self.fmt.minvalue(fix.EFormat.BIN), exp_min_bin)
        # range
        self.assertTrue(isinstance(self.fmt.fixrange, tuple))
        self.assertEqual(self.fmt.fixrange, (exp_min_float, exp_max_float))

    def test_formats(self):
        """DESCR: Test the formats."""

        # tuple
        self.assertTrue(isinstance(self.fmt.tuplefmt, tuple))
        # list
        self.assertTrue(isinstance(self.fmt.listfmt, list))

    def test_inclusion(self):
        """DESCR: Test inclusion of values in representable range."""

        self.assertTrue(0 in self.fmt)
        self.assertFalse(2**self.fmt.int_bits+1 in self.fmt)
        # ensure the range limits are included
        self.assertTrue(self.fmt.maxvalue() in self.fmt)
        self.assertTrue(self.fmt.minvalue() in self.fmt)


if __name__ == '__main__':
    utst.main()
