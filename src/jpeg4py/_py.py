"""
Copyright (c) 2014, Samsung Electronics Co.,Ltd.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of Samsung Electronics Co.,Ltd..
"""

"""
jpeg4py - libjpeg-turbo cffi bindings and helper classes.
URL: https://github.com/ajkxyz/jpeg4py
Original author: Alexey Kazantsev <a.kazantsev@samsung.com>
"""

"""
Helper classes for libjpeg-turbo cffi bindings.
"""
import jpeg4py._cffi as jpeg
from jpeg4py._cffi import TJPF_RGB
import numpy
import os


class JPEGRuntimeError(RuntimeError):
    def __init__(self, msg, code):
        super(JPEGRuntimeError, self).__init__(msg)
        self.code = code


class Base(object):
    """Base class.

    Attributes:
        lib_: cffi handle to loaded shared library.
    """
    def __init__(self, lib_):
        """Constructor.

        Parameters:
            lib_: cffi handle to loaded shared library.
        """
        if lib_ is None:
            jpeg.initialize()
            lib_ = jpeg.lib
        self.lib_ = lib_

    def get_last_error(self):
        """Returns last error string.
        """
        return jpeg.ffi.string(self.lib_.tjGetErrorStr()).decode("utf-8")


class Handle(Base):
    """Stores tjhandle pointer.

    Attributes:
        handle_: cffi tjhandle pointer.
    """
    def __init__(self, handle_, lib_):
        """Constructor.

        Parameters:
            handle_: cffi tjhandle pointer.
        """
        self.handle_ = None
        super(Handle, self).__init__(lib_)
        self.handle_ = handle_

    def release(self):
        if self.handle_ is not None:
            self.lib_.tjDestroy(self.handle_)
            self.handle_ = None


class JPEG(Base):
    """Main class.

    Attributes:
        decompressor: Handle object for decompressor.
        source: numpy array with source data,
                either encoded raw jpeg which may be decoded/transformed or
                or source image for the later encode.
        width: image width.
        height: image height.
        subsampling: level of chrominance subsampling.

    Static attributes:
        decompressors: list of decompressors for caching purposes.
    """
    decompressors = []

    @staticmethod
    def clear():
        """Clears internal caches.
        """
        # Manually release cached JPEG decompressors
        for handle in reversed(JPEG.decompressors):
            handle.release()
        del JPEG.decompressors[:]

    def __init__(self, source, lib_=None):
        """Constructor.

        Parameters:
            source: source for JPEG operations (numpy array or file name).
        """
        super(JPEG, self).__init__(lib_)
        self.decompressor = None
        self.width = None
        self.height = None
        self.subsampling = None
        if hasattr(source, "__array_interface__"):
            self.source = source
        elif numpy.fromfile is not None:
            self.source = numpy.fromfile(source, dtype=numpy.uint8)
        else:
            fin = open(source, "rb")
            self.source = numpy.empty(os.path.getsize(source),
                                      dtype=numpy.uint8)
            fin.readinto(self.source)
            fin.close()

    def _get_decompressor(self):
        if self.decompressor is not None:
            return
        try:
            self.decompressor = JPEG.decompressors.pop(-1)
        except IndexError:
            d = self.lib_.tjInitDecompress()
            if d == jpeg.ffi.NULL:
                raise JPEGRuntimeError(
                    "tjInitDecompress() failed with error "
                    "string %s" % self.get_last_error(), 0)
            self.decompressor = Handle(d, self.lib_)

    def parse_header(self):
        """Parses JPEG header.

        Fills self.width, self.height, self.subsampling.
        """
        self._get_decompressor()
        whs = jpeg.ffi.new("int[]", 3)
        whs_base = int(jpeg.ffi.cast("size_t", whs))
        whs_itemsize = int(jpeg.ffi.sizeof("int"))
        n = self.lib_.tjDecompressHeader2(
            self.decompressor.handle_,
            jpeg.ffi.cast("unsigned char*",
                          self.source.__array_interface__["data"][0]),
            self.source.nbytes,
            jpeg.ffi.cast("int*", whs_base),
            jpeg.ffi.cast("int*", whs_base + whs_itemsize),
            jpeg.ffi.cast("int*", whs_base + whs_itemsize + whs_itemsize))
        if n:
            raise JPEGRuntimeError("tjDecompressHeader2() failed with error "
                                   "%d and error string %s" %
                                   (n, self.get_last_error()), n)
        self.width = int(whs[0])
        self.height = int(whs[1])
        self.subsampling = int(whs[2])

    def decode(self, dst=None, pixfmt=TJPF_RGB):
        bpp = jpeg.tjPixelSize[pixfmt]
        if dst is None:
            if self.width is None:
                self.parse_header()
            sh = [self.height, self.width]
            if bpp > 1:
                sh.append(bpp)
            dst = numpy.zeros(sh, dtype=numpy.uint8)
        elif not hasattr(dst, "__array_interface__"):
            raise ValueError("dst should be numpy array or None")
        if len(dst.shape) < 2:
            raise ValueError("dst shape length should 2 or 3")
        if dst.nbytes < dst.shape[1] * dst.shape[0] * bpp:
            raise ValueError(
                "dst is too small to hold the requested pixel format")
        self._get_decompressor()
        n = self.lib_.tjDecompress2(
            self.decompressor.handle_,
            jpeg.ffi.cast("unsigned char*",
                          self.source.__array_interface__["data"][0]),
            self.source.nbytes,
            jpeg.ffi.cast("unsigned char*",
                          dst.__array_interface__["data"][0]),
            dst.shape[1], dst.strides[0], dst.shape[0], pixfmt, 0)
        if n:
            raise JPEGRuntimeError("tjDecompress2() failed with error "
                                   "%d and error string %s" %
                                   (n, self.get_last_error()), n)
        return dst

    def __del__(self):
        # Return decompressor to cache.
        if self.decompressor is not None:
            JPEG.decompressors.append(self.decompressor)
