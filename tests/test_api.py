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
Tests some of the api in jpeg4py package.
"""
import unittest
import logging
import jpeg4py as jpeg
import numpy
import os
import gc


class Test(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        dirnme = os.path.dirname(__file__)
        fnme = os.path.join(dirnme, "test.jpg") if len(dirnme) else "test.jpg"
        fin = open(fnme, "rb")
        self.raw = numpy.empty(os.path.getsize(fnme), dtype=numpy.uint8)
        fin.readinto(self.raw)
        fin.close()

    def tearDown(self):
        pass

    def test_initialize(self):
        jpeg.initialize()
        lib = jpeg.lib
        jpeg.initialize()
        self.assertEqual(jpeg.lib, lib)

    def test_constants(self):
        self.assertEqual(jpeg.TJSAMP_444, 0)
        self.assertEqual(jpeg.TJSAMP_422, 1)
        self.assertEqual(jpeg.TJSAMP_420, 2)
        self.assertEqual(jpeg.TJSAMP_GRAY, 3)
        self.assertEqual(jpeg.TJSAMP_440, 4)
        self.assertEqual(jpeg.TJPF_RGB, 0)
        self.assertEqual(jpeg.TJPF_BGR, 1)
        self.assertEqual(jpeg.TJPF_RGBX, 2)
        self.assertEqual(jpeg.TJPF_BGRX, 3)
        self.assertEqual(jpeg.TJPF_XBGR, 4)
        self.assertEqual(jpeg.TJPF_XRGB, 5)
        self.assertEqual(jpeg.TJPF_GRAY, 6)
        self.assertEqual(jpeg.TJPF_RGBA, 7)
        self.assertEqual(jpeg.TJPF_BGRA, 8)
        self.assertEqual(jpeg.TJPF_ABGR, 9)
        self.assertEqual(jpeg.TJPF_ARGB, 10)

    def test_parse_header(self):
        raw = self.raw.copy()
        jp = jpeg.JPEG(raw)
        jp.parse_header()
        self.assertIsNotNone(jp.width)
        self.assertIsNotNone(jp.height)
        self.assertIsNotNone(jp.subsampling)
        return jp

    def test_clear(self):
        gc.collect()
        jp = self.test_parse_header()
        jp2 = self.test_parse_header()
        del jp
        gc.collect()
        self.assertEqual(len(jpeg.JPEG.decompressors), 1)
        del jp2
        gc.collect()
        self.assertEqual(len(jpeg.JPEG.decompressors), 2)
        jp = self.test_parse_header()
        self.assertEqual(len(jpeg.JPEG.decompressors), 1)
        del jp
        gc.collect()
        jpeg.JPEG.clear()
        self.assertEqual(len(jpeg.JPEG.decompressors), 0)
        jp = self.test_parse_header()
        self.assertEqual(len(jpeg.JPEG.decompressors), 0)
        del jp
        gc.collect()

    def test_decode(self):
        jp = self.test_parse_header()
        a = jp.decode()
        self.assertEqual(len(a.shape), 3)
        self.assertEqual(a.shape[0], jp.height)
        self.assertEqual(a.shape[1], jp.width)
        self.assertEqual(a.shape[2], 3)
        a = jp.decode(pixfmt=jpeg.TJPF_GRAY)
        self.assertEqual(len(a.shape), 2)
        self.assertEqual(a.shape[0], jp.height)
        self.assertEqual(a.shape[1], jp.width)
        #import matplotlib.pyplot as pp
        #pp.axis("off")
        #pp.imshow(a)
        #pp.show()


if __name__ == "__main__":
    unittest.main()
