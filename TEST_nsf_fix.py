# ## Compare against known values

import numpy as np

from nsf_fix import FixNum as fi
from nsf_fix_util import FixFmt as fu

# ******************************
# TEST ROUND METHODS - SIGNED
# ******************************

# define format
s_4 = fu(True, 0, 4)
# create test vector
realCoeff = 2**s_4.fracBits
tstPatternSigned = np.array([2.6, 2.5, 2.4, 1.7, 1.5, 1.2,
                            -4.3, -4.5, -4.8, -5.4, -5.5, -5.6]) / realCoeff
# expected values
tstExpSigned = {}
tstExpSigned['SymInf'] = np.array([3, 3, 2, 2, 2, 1,
                                   -4, -5, -5, -5, -6, -6]) / realCoeff
tstExpSigned['SymZero'] = np.array([3, 2, 2, 2, 1, 1,
                                    -4, -4, -5, -5, -5, -6]) / realCoeff
tstExpSigned['NonSymPos'] = np.array([3, 3, 2, 2, 2, 1,
                                      -4, -4, -5, -5, -5, -6]) / realCoeff
tstExpSigned['NonSymNeg'] = np.array([3, 2, 2, 2, 1, 1,
                                      -4, -5, -5, -5, -6, -6]) / realCoeff
tstExpSigned['ConvEven'] = np.array([3, 2, 2, 2, 2, 1,
                                     -4, -4, -5, -5, -6, -6]) / realCoeff
tstExpSigned['ConvOdd'] = np.array([3, 3, 2, 2, 1, 1,
                                    -4, -5, -5, -5, -5, -6]) / realCoeff
tstExpSigned['Floor'] = np.array([2, 2, 2, 1, 1, 1,
                                  -4, -4, -4, -5, -5, -5]) / realCoeff

# apply round methods on test pattern
tstFixSigned = {key: fi(tstPatternSigned, s_4, key, 'Wrap')
                for key in tstExpSigned.keys()}

# verify
resTestMethodsSigned = {key: 'ok' if False not in
                        (tstExpSigned[key] == tstFixSigned[key].value)
                        else 'WRONG' for key in tstExpSigned.keys()}

# ******************************
# TEST ROUND METHODS - UNSIGNED
# ******************************
# define format
u_4 = fu(False, 0, 4)
# create test vector
realCoeff = 2**s_4.fracBits
tstPatternUnsigned = np.array([2.6, 2.5, 2.4, 1.7, 1.5, 1.2,
                               4.3,  4.5,  4.8,  5.4,  5.5,  5.6]) / realCoeff

# expected values
tstExpUnsigned = {}
tstExpUnsigned['SymInf'] = np.array([3, 3, 2, 2, 2, 1,
                                     4, 5, 5, 5, 6, 6]) / realCoeff
tstExpUnsigned['SymZero'] = np.array([3, 2, 2, 2, 1, 1,
                                      4, 4, 5, 5, 5, 6]) / realCoeff
tstExpUnsigned['NonSymPos'] = np.array([3, 3, 2, 2, 2, 1,
                                        4, 5, 5, 5, 6, 6]) / realCoeff
tstExpUnsigned['NonSymNeg'] = np.array([3, 2, 2, 2, 1, 1,
                                        4, 4, 5, 5, 5, 6]) / realCoeff
tstExpUnsigned['ConvEven'] = np.array([3, 2, 2, 2, 2, 1,
                                       4, 4, 5, 5, 6, 6]) / realCoeff
tstExpUnsigned['ConvOdd'] = np.array([3, 3, 2, 2, 1, 1,
                                      4, 5, 5, 5, 5, 6]) / realCoeff
tstExpUnsigned['Floor'] = np.array([2, 2, 2, 1, 1, 1,
                                    4, 4, 4, 5, 5, 5]) / realCoeff

# apply round methods on test pattern
tstFixUnsigned = {key: fi(tstPatternUnsigned, u_4, key, 'Wrap')
                  for key in tstExpUnsigned.keys()}

# verify
resTestMethodsUnsigned = {key: 'ok' if False not in
                          (tstExpUnsigned[key] == tstFixUnsigned[key].value)
                          else 'WRONG' for key in tstExpUnsigned.keys()}


# ******************************
# TEST OVERFLOW METHODS - SIGNED
# ******************************
# saturation overflow
# max 0.9375 min -1
overPatternSigned = np.array([1, 2, 3.0001, 1-2**(-4), 1-2**(-5), 1-2**(-3),
                              -1, -1-2**(-4)])
overExpSigned = {}
overExpSigned['Sat'] = np.array([.9375, .9375, .9375, .9375, .9375, .875,
                                 -1, -1])
# wrap overflow
overExpSigned['Wrap'] = np.array([-1, 0, -1, .9375, .9375, .875,
                                  -1, .9375])

# apply overflow methods
overFixSigned = {key: fi(overPatternSigned, s_4, 'SymZero', key)
                 for key in overExpSigned.keys()}

# verify
resTestOverSigned = {key: 'ok' if False not in
                     (overExpSigned[key] == overFixSigned[key].value)
                     else 'WRONG' for key in overExpSigned.keys()}

# ******************************
# TEST OVERFLOW METHODS - UNSIGNED
# ******************************
# saturation overflow
# max 0.9375 min 0
overPatternUnsigned = np.array([1, 2, 3.0001, 1-2**(-4), 1-2**(-5), 1-2**(-3),
                                -1, -1-2**(-4)])
overExpUnsigned = {}
overExpUnsigned['Sat'] = np.array([.9375, .9375, .9375, .9375, .9375, .875,
                                   0, 0])

# wrap overflow
overExpUnsigned['Wrap'] = np.array([0, 0, 0, .9375, .9375, .875,
                                    0, .9375])

# apply overflow methods
overFixUnsigned = {key: fi(overPatternUnsigned, u_4, 'SymZero', key)
                   for key in overExpUnsigned.keys()}

# verify
resTestOverUnsigned = {key: 'ok' if False not in
                       (overExpUnsigned[key] == overFixUnsigned[key].value)
                       else 'WRONG' for key in overExpUnsigned.keys()}
