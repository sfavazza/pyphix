# ## Compare fix number against commercial matlab data series
# # Test conditions
#
# - 2^20-1 values
# - signed interval: -1.2 to 1.2
# - unsigned interval: -0.2 to 1.2
# - signed fmt: (t,0,15)
# - unsigned fmt: (f,0,16)
import glob
import os
import sys
sys.path.append('..')

import numpy as np
import matplotlib.pyplot as plt

import nsf_fix as fi
import nsf_fix_util as fu

tst_file_lst_u = glob.glob('u_*.txt')
tst_file_lst_s = glob.glob('s_*.txt')

# Define matlab dicts
num_lst_u = {}
num_lst_s = {}
# Read from text files unsigned
print("INFO: Read unsigned value series files...")
for filename in tst_file_lst_u:
    with open(filename, 'r') as f:
        (name, extension) = os.path.splitext(filename)
        # remove new line characters
        num_lst_u[name] = [np.float(k.rstrip()) for k in f.readlines()]

print("\t...complete")

# Read from text files signed
print("INFO: Read unsigned value series files...")
for filename in tst_file_lst_s:
    with open(filename, 'r') as f:
        (name, extension) = os.path.splitext(filename)
        # remove new line characters
        num_lst_s[name] = [np.float(k.rstrip()) for k in f.readlines()]

print("\t...complete")

# Create value series for test
u_series = np.linspace(-.2, 1.2, 2**18-1)
s_series = np.linspace(-1.2, 1.2, 2**18-1)

# Define nsf_fix dicts
fix_lst_u = {}
fix_lst_s = {}

u_16 = fu.FixFmt(False, 0, 16)
s_16 = fu.FixFmt(True, 0, 16)

# Define fimath correspondence between matlab and nsf_fix
fimath_dict = {'ceil': 'Ceil',
               'convergent': 'ConvOdd',
               'fix': 'Floor',
               'floor': 'NonSymNeg',
               'nearest': 'NonSymPos',
               'round': 'SymInf',
               'saturate': 'Sat',
               'wrap': 'Wrap'}

# create fix value series for test
print("INFO: Generate unsigned fix value series...")
for fimath in num_lst_u.keys():
    split_key = fimath.split('_')
    fix_lst_u[fimath] = fi.FixNum(u_series, u_16,
                                  fimath_dict[split_key[-2]],  # round
                                  fimath_dict[split_key[-1]])  # overflow

print("\t...complete")

print("INFO: Generate signed fix value series...")
for fimath in num_lst_s.keys():
    split_key = fimath.split('_')
    fix_lst_s[fimath] = fi.FixNum(s_series, s_16,
                                  fimath_dict[split_key[-2]],  # round
                                  fimath_dict[split_key[-1]])  # overflow

print("\t...complete")

# compare the two representations
results_u = {key: 'correct' if False not in
             (fix_lst_u[key].value == num_lst_u[key]) else 'wrong'
             for key in fix_lst_u.keys()}

results_s = {key: 'correct' if False not in
             (fix_lst_s[key].value == num_lst_s[key]) else 'wrong'
             for key in fix_lst_s.keys()}

# plot all fix lists
# keys_u = tuple(fix_lst_u)
# plt.plot(u_series, fix_lst_u[keys_u[0]].value,
#          u_series, fix_lst_u[keys_u[1]].value,
#          u_series, fix_lst_u[keys_u[2]].value)
# plt.title(keys_u[0] + ' ' + keys_u[1] + ' ' + keys_u[2])
