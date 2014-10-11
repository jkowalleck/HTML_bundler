#!/usr/bin/env python

""" test Bundler.__preserve_html_entities
     and Bundler.__revert_html_entities """

import unittest

from bundler import Bundler


### class inherited for access to private funcs

class Test_Bundler(Bundler):
    @classmethod
    def preserve_html_entities(cls, string):
        return cls._preserve_html_entities(string)
    @classmethod
    def revert_html_entities(cls, string):
        return cls._revert_html_entities(string)


### test

class Test(unittest.TestCase):

    ### helper functions

    @staticmethod
    def _back_and_forth(string):
        preserved = Test_Bundler.preserve_html_entities(string)
        reverted = Test_Bundler.revert_html_entities(preserved)
        return reverted

    ### tests

    def test_none(self):
        string = ""
        self.assertEqual(string, self._back_and_forth(string))

    def test_nothing(self):
        string = "foo bar"
        self.assertEqual(string, self._back_and_forth(string))

    def test_numeric(self):
        string = "foo &#1337; bar"
        self.assertEqual(string, self._back_and_forth(string))

    def test_hex(self):
        string = "foo &#xf00; bar"
        self.assertEqual(string, self._back_and_forth(string))

    def test_name(self):
        string = "foo &amp; bar"
        self.assertEqual(string, self._back_and_forth(string))

    def test_multiple(self):
        string = "foo &hellip; bar &#42; baz &#xB14; qux"
        self.assertEqual(string, self._back_and_forth(string))

    def test_suspect(self):
        string = "foo &amp; bar"
        string = Test_Bundler.preserve_html_entities(string)
        self.assertEqual(string, self._back_and_forth(string))

    def test_suspect_double(self):
        string = "foo &amp; bar"
        string = Test_Bundler.preserve_html_entities(string)
        string = Test_Bundler.preserve_html_entities(string)
        self.assertEqual(string, self._back_and_forth(string))

if __name__ == '__main__':
    unittest.main()