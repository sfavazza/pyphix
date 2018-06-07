import unittest as utst
import importlib as imp

from pyphix import fix as fi

# reload module to be sure last changes are taken into account
imp.reload(fi)


class TestFixFmtMethods(utst.TestCase):

    # define fmt object under test
    fmt = fi.FixFmt(True, 21, 4)

    def test_properties(self):
        # bit number
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


if __name__ == '__main__':
    utst.main()
