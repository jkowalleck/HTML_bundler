""" unit test for Bundler.strip_marked_line_from_css_or_js """


import unittest


from bundler import Bundler


class Test_strip_marked_line_from_css_or_js(unittest.TestCase):

    def test_none(self):
        string = "nothing to change here"
        self.assertEqual(string, Bundler.strip_marked_line_from_css_or_js(string, ""))


    def test_single(self):
        string = "this should be empty // @strip"
        self.assertEqual("", Bundler.strip_marked_line_from_css_or_js(string, "strip"))