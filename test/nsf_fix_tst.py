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
import re
import sys
sys.path.append('..')

import numpy as np
import matplotlib.pyplot as plt

import nsf_fix as fi
import nsf_fix_util as fu

# list test set files
tst_file_lst_u = glob.glob('u_*.txt')
tst_file_lst_s = glob.glob('s_*.txt')
tst_file_lst_u.remove('u_src.txt')
tst_file_lst_s.remove('s_src.txt')

# Read value series for test
with open('u_src.txt', 'r') as f:
    u_series = np.array([np.float(k.rstrip()) for k in f.readlines()])
with open('s_src.txt', 'r') as f:
    s_series = np.array([np.float(k.rstrip()) for k in f.readlines()])

# filter only values that when converted in fix point arithmetic has first
# digit after point equal to 5
u_series_str = [str(k*2**16) for k in u_series]
s_series_str = [str(k*2**16) for k in s_series]
u_idx_05 = [el for el in range(0, len(u_series_str))
            if re.search('\.5', u_series_str[el]) is not None]
s_idx_05 = [el for el in range(0, len(s_series_str))
            if re.search('\.5', s_series_str[el]) is not None]
u_series = u_series[u_idx_05]
s_series = s_series[s_idx_05]

# Define matlab dicts
num_lst_u = {}
num_lst_s = {}
# Read from text files unsigned
print("INFO: Read unsigned value series files...")
for filename in tst_file_lst_u:
    with open(filename, 'r') as f:
        (name, extension) = os.path.splitext(filename)
        # remove new line characters
        num_lst_u[name] = np.array([np.float(k.rstrip())
                                    for k in f.readlines()])
        num_lst_u[name] = num_lst_u[name][u_idx_05]

print("\t...complete")

# Read from text files signed
print("INFO: Read signed value series files...")
for filename in tst_file_lst_s:
    with open(filename, 'r') as f:
        (name, extension) = os.path.splitext(filename)
        # remove new line characters
        num_lst_s[name] = np.array([np.float(k.rstrip())
                                    for k in f.readlines()])
        num_lst_s[name] = num_lst_s[name][s_idx_05]

print("\t...complete")


u_16 = fu.FixFmt(False, 0, 16)
s_16 = fu.FixFmt(True, 0, 15)

# Define nsf_fix dicts
fix_lst_u = {}
fix_lst_s = {}

# Define fimath correspondence between matlab and nsf_fix
fimath_dict = {'ceil': 'Ceil',
               'convergent': 'ConvOdd',  # never met
               'fix': 'SymZero',
               'floor': 'Floor',      # NonSymNeg
               'nearest': 'NonSymPos',  # ConvEven
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

