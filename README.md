jpeg4py
=======

Python cffi libjpeg-turbo bindings and helper classes.

The purpose of this package is to provide thread-safe and aware of GIL Python
bindings to libjpeg-turbo which work with numpy arrays on
Python 2, 3 and PyPy (when numpy is fully implemented). It was tested with
Python 2.7, Python 3.3 and PyPy on Ubuntu 13.10.


Covered TurboJPEG API:
```
tjInitDecompress
tjDecompressHeader2
tjDecompress2
```
so, currently, only decoding of jpeg files is possible, and
it is about 1.3 times faster than Image.open().tobytes() and
scipy.misc.imread() in a single thread and up to 9 times faster in
multithreaded mode.


Installation
------------

Requirements:

1. numpy
2. libjpeg-turbo

On Ubuntu, the shared library is included in libturbojpeg package:
```bash
sudo apt-get install libturbojpeg
```
If you have a custom library which is TurboJPEG API compatible,
just call jpeg4py.initialize with tuple containing that library's file name.

To install the module run:
```bash
python setup.py install
```
or just copy src/jpeg4py to any place where python interpreter will be able
to find it.

Tests
-----

To run the tests, execute:

for Python 2.7:
```bash
PYTHONPATH=src nosetests -w tests
```
for Python 3.3:
```bash
PYTHONPATH=src nosetests3 -w tests
```
for PyPy:
```bash
PYTHONPATH=src pypy tests/test_api.py
```

Example usage:
--------------

```python
import jpeg4py as jpeg
import matplotlib.pyplot as pp


if __name__ == "__main__":
    pp.imshow(jpeg.JPEG("test.jpg").decode())
    pp.show()
```

License
-------

Released under Simplified BSD License.
Copyright (c) 2014, Samsung Electronics Co.,Ltd.
