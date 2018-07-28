# pyPhix, the Python Fixed Point module

**pyPhix** is a python package for fixed point number representation.
It is intended to support the implementation of digital signal processing systems.
As such only fix-point addition, subtraction and multiplication operations are implemented.

You can find more information about the module objects and functionalities at
[readthedocs](https://pyphix.readthedocs.io/en/latest/) project page.

## Features

* virtually unlimited number length (depending on your RAM size)
* based on NumPy
* customizable rounding method (```SymInf```, ```SymZero```, ```NonSymPos```,
```NonSymNeg```, ```ConvEven```, ```ConvOdd```, ```Floor```, ```Ceil```)
* customizable wrapping method (```Sat```, ```Wrap```)
* support various representation formats (```bin```, ```hex```, ```int```, ```float```)
* perform single or array based operations with customizable output format (```+```, ```-```, ```*```)

## License

### pyPhix
pyPhix is an open source python module released under the terms of
[Mozilla Public License Version 2.0](LICENSE.txt).

### NumPy
**NumPy** is the fundamental package needed for scientific computing with Python and it is released under these
[terms](https://github.com/numpy/numpy/blob/master/LICENSE.txt "Numpy license").

## Install

The **pyPhix** package is available on [pypi.org](https://pypi.org/project/pyPhix).
You can install it by running:

```$ pip install pyphix```.

Alternatively you can clone the **pyPhix** repository and from the folder containing the *setup.py* file run:

```$ python setup install```

This package requires Python 3.6 to work.

You can also directly download the tar.gz archive from [pypi.org](https://pypi.org/project/pyPhix#files).
The archive can be easily verified by adding the gpg public key
[1E948096166391C0](https://pgp.mit.edu/pks/lookup?op=vindex&search=0x1E948096166391C0)
to your keyring.

## Usage Examples

### Fix Format

This object is used to indicate the number of bits the user wants to use for value reprensetation.

Create fix-point format objets:
```
>>> from pyphix import fix
>>> fmt_a=fix.FixFmt(True, 2, 10)
>>> fmt_b=fix.FixFmt(False, 0, 7)
```

Print the maximum representable ranges and test if a value is included in the range:
```
>>> fmt_a.fixrange
(-4.0, 3.9990234375)

>>> fmt_b.fixrange
(0.0, 0.9921875)

>>> -10 in fmt_a
False

>>> 0 in fmt_b
True
```

Different representations are available:
```
>>> fmt_a.tuplefmt
(True, 2, 10)

>>> fmt_b.listfmt
[False, 0, 7]

>>> print(fmt_b)
(False, 0, 7)
```

### Fix Number

This object contain fix-point number represenation.

Round methods comparison, assuming format *(True, 4, 5)*:

| Round method  | Pos odd fraction | Pos even fraction | Neg odd fraction | Neg even fraction |
|---------------|:----------------:|:-----------------:|:----------------:|:-----------------:|
|**Real value** |7.296875          |2.325              |-1.078125         |-1.08125           |
|**Mult by 2^5**|233.5             |74.4               |-34.5             |-34.6              |
|```SymInf```   |7.3125            |2.3125             |-1.09375          |-1.09375           |
|```SymZero```  |7.28125           |2.3125             |-1.0625           |-1.09375           |
|```NonSymPos```|7.3125            |2.3125             |-1.0625           |-1.09375           |
|```NonSymNeg```|7.28125           |2.3125             |-1.09375          |-1.09375           |
|```ConvEven``` |7.3125            |2.3125             |-1.0625           |-1.09375           |
|```ConvOdd```  |7.28125           |2.3125             |-1.09375          |-1.09375           |
|```Floor```    |7.28125           |2.3125             |-1.09375          |-1.09375           |
|```Ceil```     |7.3125            |2.34375            |-1.0625           |-1.0625            |

A small usage example:
```
>>> from pyphix import fix
>>> from pyphix.fix import ERoundMethod, EOverMethod
>>> fmt = fix.FixFmt(True, 4, 5)
>>> fix_vec = fix.FixNum(
        [7.296875,  2.325   , -1.078125, -1.08125], fmt,
        rnd=ERoundMethod.CONV_ODD, over=EOverMethod.WRAP)
>>> fix_val = fix.FixNum(
        1.16, fmt,
        rnd=ERoundMethod.CONV_ODD, over=EOverMethod.WRAP)
```

Perform a full resolution addition:
```
>>> fix_vec + fix_val
[8.4375  3.46875 0.0625  0.0625 ]

  fmt: (True, 5, 5)
  rnd: ERoundMethod.CONV_ODD
  over: EOverMethod.WRAP
```

Perform a multiplication and cast result to a small format:
```
>>> fix_val.mult(
        fix_vec, out_fmt=fix.FixFmt(False, 3, 2),
        rnd=ERoundMethod.SYM_INF, over=EOverMethod.SAT)
[7.75 2.75 0.   0.  ]

  fmt: (False, 3, 2)
  rnd: ERoundMethod.SYM_INF
  over: EOverMethod.SAT
```
