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
jpeg4py.JPEG().decode() vs scipy.misc.imread() vs Image.open().tobytes()
"""
import unittest
import logging
import jpeg4py as jpeg
import os
import time
import threading
import scipy.misc
try:
    import Image
    no_pil = False
except ImportError:
    no_pil = True


class Test(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.dirnme = os.path.dirname(__file__)
        self.fnme = (os.path.join(self.dirnme, "1024.jpg") if len(self.dirnme)
                     else "1024.jpg")

    def tearDown(self):
        pass

    def looped(self, target, n):
        for i in range(n):
            target()

    def bench(self, target, n_threads, n):
        t0 = time.time()
        th = []
        for i in range(n_threads):
            th.append(threading.Thread(target=self.looped, args=(target, n)))
            th[-1].start()
        for t in th:
            t.join()
        return time.time() - t0

    def bench_jpeg4py(self):
        a = jpeg.JPEG(self.fnme).decode()
        del a

    def bench_scipy(self):
        a = scipy.misc.imread(self.fnme)
        del a

    def bench_pil(self):
        a = Image.open(self.fnme).tobytes()
        del a

    def do_bench(self, n_threads, n):
        dt_jpeg4py = self.bench(self.bench_jpeg4py, n_threads, n)
        logging.info("jpeg4py decoded %d images per thread and %d threads "
                     "in %.3f sec", n, n_threads, dt_jpeg4py)
        dt_scipy = self.bench(self.bench_scipy, n_threads, n)
        logging.info("scipy decoded %d images per thread and %d threads "
                     "in %.3f sec", n, n_threads, dt_scipy)
        global no_pil
        if not no_pil:
            dt_pil = self.bench(self.bench_pil, n_threads, n)
            logging.info("pil decoded %d images per thread and %d threads "
                         "in %.3f sec", n, n_threads, dt_pil)
            logging.info("With %d images per thread and %d threads jpeg4py vs "
                         "(scipy, pil) = (%.1f, %.1f) times", n, n_threads,
                         dt_scipy / dt_jpeg4py, dt_pil / dt_jpeg4py)
        else:
            logging.info("With %d images per thread and %d threads jpeg4py vs "
                         "scipy = %.1f times", n, n_threads,
                         dt_scipy / dt_jpeg4py)

    def test_1_thread(self):
        self.do_bench(1, 50)

    def test_2_threads(self):
        self.do_bench(2, 50)

    def test_8_threads(self):
        self.do_bench(8, 50)

    def test_32_threads(self):
        self.do_bench(32, 50)

    def test_768_threads(self):
        logging.info("Will test 768 threads on small file")
        self.fnme = (os.path.join(self.dirnme, "64.jpg") if len(self.dirnme)
                     else "64.jpg")
        self.do_bench(768, 50)


if __name__ == "__main__":
    unittest.main()
