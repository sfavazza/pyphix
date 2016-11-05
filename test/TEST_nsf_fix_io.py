import unittest as utst
import numpy as np
import importlib as imp

import nsf_fix_io as fio
import nsf_fix_util as fu
import nsf_fix as fi

########################################################
# IMPORTANT: run this script from its parent directory #
########################################################

# reload module to be sure last changes are taken into account
imp.reload(fio)
imp.reload(fu)
imp.reload(fi)


class TestNsfFixIoMethods(utst.TestCase):
    # prepare example data
    data1 = np.array(np.linspace(2, 3, 49))
    data2 = [x for x in range(0, 49)]
    data3 = fi.FixNum(
        np.linspace(-.2, .24, 49), fu.FixFmt(True, 0, 8), 'SymInf', 'Wrap')
    data4 = [int(x*10) % 2 == 0 for x in data1]
    data5 = fi.FixNum(
        [np.linspace(2, 3, 49), np.linspace(2, 3, 49)], fu.FixFmt(False, 1, 7))
    data6 = [x for x in range(1, 70)]
    data7 = data4

    def test_NsfFixIo_ColumnActions(self):
        # define file object
        objFile = fio.FixFile()

        # header is empty
        with self.assertRaises(Warning):
            objFile.get_header()

        # no columns to remove
        with self.assertRaises(ValueError):
            objFile.remove_column('whatever')

        # add columns and verify header
        objFile \
            .add_column('data1', 'int', self.data1) \
            .add_column('data2', 'float', self.data2) \
            .add_column('data3', 'fix', self.data3) \
            .add_column('data4', 'bool', self.data4)
        # verify header
        self.assertEqual(['data1', 'data2', 'data3', 'data4'],
                         objFile.get_header())
        self.assertEqual([('data1', 'int'),
                          ('data2', 'float'),
                          ('data3', 'fix'),
                          ('data4', 'bool')],
                         objFile.get_header(True))

        # remove not added column
        with self.assertRaises(ValueError):
            objFile.remove_column('notExist')

        # add column with more elements than in already added columns
        with self.assertRaises(Warning):
            objFile.add_column('data6', 'int', self.data6)

        # add column with same name of one already added
        with self.assertRaises(KeyError):
            objFile.add_column('data1', 'bool', self.data1)

        # add column twice
        with self.assertRaises(KeyError):
            objFile \
                .add_column('data7', 'bool', self.data7) \
                .add_column('data7', 'bool', self.data7)
                
        # add column with unknown type
        with self.assertRaises(ValueError):
            objFile.add_column('fakeCol', 'fakeDataType', self.data1)

        # add non-vector data column
        with self.assertRaises(ValueError):
            objFile.add_column('data5', 'fix', self.data5)
            
        # remove column
        objFile \
            .remove_column('data2') \
            .remove_column('data4')
        # verify
        self.assertEqual([('data1', 'int'),
                          ('data3', 'fix'),
                          ('data7', 'bool')], objFile.get_header(True))
        self.assertEqual(['data1', 'data3', 'data7'], objFile.get_header())

        # test write / read methods
        objFile.write('testWrite.txt')
        objReadBack = fio.FixFile()
        objReadBack.read('testWrite.txt')
        # compare headers
        self.assertEqual(objFile.get_header(), objReadBack.get_header())
        self.assertEqual(objFile.get_header(True),
                         objReadBack.get_header(True))
        # compare read values
        for col in objReadBack.get_header():
            np.testing.assert_array_equal(
                np.array(objFile.get_column(col)),
                np.array(objReadBack.get_column(col)))

if __name__ == '__main__':
    utst.main()
