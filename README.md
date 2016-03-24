jpeg4py
=======

Python cffi libjpeg-turbo bindings and helper classes.

The purpose of this package is to provide thread-safe and aware of GIL Python
bindings to libjpeg-turbo which work with numpy arrays on
Python 2, 3 and PyPy.

Tested with Python 2.7, Python 3.4 and PyPy on Ubuntu 14.04.

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

On Windows, you can download installer from the official libjpeg-turbo [Sourceforge](https://sourceforge.net/projects/libjpeg-turbo/files)
repository, install it and copy turbojpeg.dll to the directory from the system PATH.

On Mac OS X, you can download the DMG from the official libjpeg-turbo [Sourceforge](https://sourceforge.net/projects/libjpeg-turbo/files)
repository and install it.

If you have a custom library which is TurboJPEG API compatible,
just call jpeg4py.initialize with tuple containing that library's file name.

To install the module run:
```bash
python -m pip install jpeg4py
```
or
```bash
python setup.py install
```
or just copy src/jpeg4py to any place where python interpreter will be able
to find it.

Tests
-----

To run the tests, execute:
```bash
PYTHONPATH=src python -m nose -w tests
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
