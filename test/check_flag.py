""" unit test for Bundler.compress_html """

import unittest

from bundler import Bundler


class TestBundler(Bundler):

    @classmethod
    def check_flaf(cls, target, flag):
        return cls._check_flag(target, flag)


class Test_compress_html(unittest.TestCase):

    some = (1 | 2 | 3 | 4 | 8)

    def test_false(self):
        flag = 2
        target = self.some ^ flag
        self.assertFalse(TestBundler.check_flaf(target, flag))

    def test_true2(self):
        flag = 2
        target = self.some | flag
        self.assertTrue(TestBundler.check_flaf(target, flag))