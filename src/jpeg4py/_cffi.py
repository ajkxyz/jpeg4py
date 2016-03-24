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
libjpeg-turbo cffi bindings.
"""
import cffi
import threading


#: Subsumplings
TJSAMP_444 = 0
TJSAMP_422 = 1
TJSAMP_420 = 2
TJSAMP_GRAY = 3
TJSAMP_440 = 4

#: Pixel formats
TJPF_RGB = 0
TJPF_BGR = 1
TJPF_RGBX = 2
TJPF_BGRX = 3
TJPF_XBGR = 4
TJPF_XRGB = 5
TJPF_GRAY = 6
TJPF_RGBA = 7
TJPF_BGRA = 8
TJPF_ABGR = 9
TJPF_ARGB = 10


#: Pixel format to Bytes per pixel mapping
tjPixelSize = {TJPF_RGB: 3, TJPF_BGR: 3, TJPF_RGBX: 4, TJPF_BGRX: 4,
               TJPF_XBGR: 4, TJPF_XRGB: 4, TJPF_GRAY: 1, TJPF_RGBA: 4,
               TJPF_BGRA: 4, TJPF_ABGR: 4, TJPF_ARGB: 4}


#: ffi parser
ffi = None


#: Loaded shared library
lib = None


#: Lock
lock = threading.Lock()


def _initialize(backends):
    global lib
    if lib is not None:
        return
    # C function definitions
    src = """
    typedef void *tjhandle;

    typedef struct {
      int x;
      int y;
      int w;
      int h;
    } tjregion;

    typedef struct {
      tjregion r;
      int op;
      int options;
      void *data;
      void *customFilter;
    } tjtransform;

    typedef struct {
      int num;
      int denom;
    } tjscalingfactor;

    tjhandle tjInitDecompress();
    int tjDestroy(tjhandle handle);
    int tjDecompressToYUV(
        tjhandle handle,
        unsigned char *jpegBuf,
        unsigned long jpegSize,
        unsigned char *dstBuf,
        int flags);
    unsigned long tjBufSizeYUV(int width, int height, int subsamp);
    int tjDecompressHeader2(
        tjhandle handle,
        unsigned char *jpegBuf,
        unsigned long jpegSize,
        int *width,
        int *height,
        int *jpegSubsamp);
    int tjDecompress2(
        tjhandle handle,
        unsigned char *jpegBuf,
        unsigned long jpegSize,
        unsigned char *dstBuf,
        int width,
        int pitch,
        int height,
        int pixelFormat,
        int flags);
    tjhandle tjInitCompress();
    int tjCompress2(
         tjhandle handle,
         unsigned char *srcBuf,
         int width,
         int pitch,
         int height,
         int pixelFormat,
         unsigned char **jpegBuf,
         unsigned long *jpegSize,
         int jpegSubsamp,
         int jpegQual,
         int flags);
    unsigned long tjBufSize(
        int width,
        int height,
        int jpegSubsamp);
    int tjEncodeYUV2(
        tjhandle handle,
        unsigned char *srcBuf,
        int width,
        int pitch,
        int height,
        int pixelFormat,
        unsigned char *dstBuf,
        int subsamp,
        int flags);
    char* tjGetErrorStr();
    tjhandle tjInitTransform();
    int tjTransform(
        tjhandle handle,
        unsigned char *jpegBuf,
        unsigned long jpegSize,
        int n,
        unsigned char **dstBufs,
        unsigned long *dstSizes,
        tjtransform *transforms,
        int flags);
    unsigned char *tjAlloc(int bytes);
    void tjFree(unsigned char *buffer);
    tjscalingfactor *tjGetScalingFactors(int *numscalingfactors);
    """

    # Parse
    global ffi
    ffi = cffi.FFI()
    ffi.cdef(src)

    # Load library
    for libnme in backends:
        try:
            lib = ffi.dlopen(libnme)
            break
        except OSError:
            pass
    else:
        ffi = None
        raise OSError("Could not load libjpeg-turbo library")


def initialize(
        backends=(
        "libturbojpeg.so.0",  # for Ubuntu
        "turbojpeg.dll",  # for Windows
        "/opt/libjpeg-turbo/lib64/libturbojpeg.0.dylib",  # for Mac OS X
        )):
    """Loads the shared library if it was not loaded yet.

    Parameters:
        backends: tuple of shared library file names to try to load.
    """
    global lib
    if lib is not None:
        return
    global lock
    with lock:
        _initialize(backends)
