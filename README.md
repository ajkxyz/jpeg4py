jpeg4py
=======

Python cffi libjpeg-turbo bindings and helper classes.

Tested with Python 2.7, Python 3.3 and PyPy on Ubuntu 13.10.

The purpose of this package is to provide thread-safe with releasing of GIL
bindings for libjpeg-turbo which will work with numpy arrays on
Python 2, 3 and PyPy with included numpy.


Covered TurboJPEG API:
```
tjInitDecompress
tjDecompressHeader2
tjDecompress2
```


Requirements:

1. numpy.

2. Python bindings use TurboJPEG API, so the shared library should include it.

On Ubuntu 13.10 the correct shared library is included in libturbojpeg package:
```bash
sudo apt-get install libturbojpeg
```

If you have custom library which is TurboJPEG API compartible,
just call jpeg4py.initialize with tuple containing that library file name.


To install the module run:
```bash
python setup.py install
```
or just copy src/jpeg4py to any place where python
interpreter will be able to find it.


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

```python
import jpeg4py as jpeg
import matplotlib.pyplot as pp


if __name__ == "__main__":
    pp.imshow(jpeg.JPEG("test.jpg").decode())
    pp.show()
```


Released under Simplified BSD License.
Copyright (c) 2014, Samsung Electronics Co.,Ltd.
