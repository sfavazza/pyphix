import importlib as imp

import numpy as np

import nsf_fix_io as fio
import nsf_fix_util as fu
import nsf_fix as fi

imp.reload(fio)
imp.reload(fu)
imp.reload(fi)

# prepare example data
data1 = np.array(np.linspace(2, 3, 49))
data2 = [x for x in range(0, 49)]
data3 = fi.FixNum(
    np.linspace(-.2, .24, 49), fu.FixFmt(True, 0, 8), 'SymInf', 'Wrap')

# define file object
objFile = fio.FixFile()

# test all methods
try:
    objFile.remove_column('data1')  # error: no columns to remove
except ValueError:
    print("_NOTE_: Test passed 1")

try:
    objFile.add_column('data1', '_wrong_format_', data1)  # error: wrong format
except ValueError:
    print("_NOTE_: Test passed 2")

objFile.add_column('data1', 'int', data1)
try:
    objFile.add_column('data1', 'fix', data1)       # error: already added
except KeyError:
    print("_NOTE_: Test passed 3")

objFile.add_column('data2', 'int', data2)
objFile.add_column('data3', 'fix', data3)

try:
    # error: lenght not correct
    objFile.add_column('datBool', 'bool', [True, False])
except Warning:
    print("_NOTE_: Test passed 4")

data4 = [np.linspace(2, 3, 49), [x for x in range(0, 49)]]
data5 = fi.FixNum(
    [np.linspace(2, 3, 49), np.linspace(2, 3, 49)], fu.FixFmt(False, 1, 7))
try:
    # error: wrong data dimension (int)
    objFile.add_column('data4', 'int', data4)
except ValueError:
    print("_NOTE_: Test passed 4")

try:
    # error: wrong data dimension (fix)
    objFile.add_column('data5', 'fix', data5)
except ValueError:
    print("_NOTE_: Test passed 5")

print(objFile.get_header())
objFile.remove_column('data1')
print(objFile.get_header())
