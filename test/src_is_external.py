""" test Bundler.src_is_external """

import unittest

from bundler import Bundler


class Test_src_is_external(unittest.TestCase):

    def test_none(self):
        string = ""
        self.assertFalse(Bundler.src_is_external(string))

    def test_relative(self):
        string = "some/path"
        self.assertFalse(Bundler.src_is_external(string))

    def test_relative_back(self):
        string = "../some/path"
        self.assertFalse(Bundler.src_is_external(string))

    def test_relative_root(self):
        string = "/some/path"
        self.assertFalse(Bundler.src_is_external(string))

    def test_relative_double(self):
        string = "some//path/"
        self.assertFalse(Bundler.src_is_external(string))

    def test_relative_suspisious(self):
        string = "some/path?foo://bar"
        self.assertFalse(Bundler.src_is_external(string))

    def test_absolute_protocol(self):
        string = "http://myserver"
        self.assertTrue(Bundler.src_is_external(string))

    def test_absolute_no_protocol(self):
        string = "//myserver"
        self.assertTrue(Bundler.src_is_external(string))

    def test_absolute_no_prototol_port(self):
        string = "//myserver:1337"
        self.assertTrue(Bundler.src_is_external(string))

    def test_absolute_no_prototol_auth(self):
        string = "//name:passwd@myserver"
        self.assertTrue(Bundler.src_is_external(string))

if __name__ == '__main__':
    unittest.main()