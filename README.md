# pyFiPo, the Python Fixed Point module

**pyFiPo** is a python package for fixed point number representation.
It is intended to support the implementation of digital signal processing systems.

## Features

* virtually unlimited number length (depending on your RAM size)
* based on NumPy
* customizable rounding method (```SymInf```, ```SymZero```, ```NonSymPos```,
```NonSymNeg```, ```ConvEven```, ```ConvOdd```, ```Floor```, ```Ceil```)
* customizable wrapping method (```Sat```, ```Wrap```)
* support various representation formats (```bin```, ```hex```, ```int```, ```float```)
* perform single or array based operations with customizable output format (```+```, ```-```, ```*```)

## License

### pyFiPo
pyFiPo is an open source python module released under the terms of
[Mozilla Public License Version 2.0](LICENSE.txt).

### NumPy
**NumPy** is the fundamental package needed for scientific computing with Python and it is released under these
[terms](https://github.com/numpy/numpy/blob/master/LICENSE.txt "Numpy license").
