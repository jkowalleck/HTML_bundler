""" test Bundler._js_comments_endline2block """

import unittest

from bundler import Bundler


### class inherited for access to protected funcs


class TestBundler(Bundler):

    @classmethod
    def js_comments_endline2block(cls, string):
        return cls._js_comments_endline2block(string)


### test

class Test_js_comments_endline2block(unittest.TestCase):

    def test_empty(self):
        string = ""
        self.assertEqual(string, TestBundler.js_comments_endline2block(string))

    def test_no_comment(self):
        string = "var i = 1;"
        self.assertEqual(string, TestBundler.js_comments_endline2block(string))

    def test_block_comment_single_line(self):
        string = "/* i am a block */"
        self.assertEqual(string, TestBundler.js_comments_endline2block(string))

    def test_block_comment_multi_line(self):
        string = "/* i am\n" \
                 " a block */"
        self.assertEqual(string, TestBundler.js_comments_endline2block(string))

    def test_block_comment_multi_line_suspicious(self):
        string = "/* i am // just\n" \
                 " a block */"
        self.assertEqual(string, TestBundler.js_comments_endline2block(string))

    def test_string_suspicious_sq(self):
        string = "var s =  'i am // no comment */';"
        self.assertEqual(string, TestBundler.js_comments_endline2block(string))

    def test_string_suspicious_dq(self):
        string = 'var s =  "i am // no comment */";'
        self.assertEqual(string, TestBundler.js_comments_endline2block(string))

    def test_endline_comment1(self):
        string = "// i am a comment"
        string_conv = "/* i am a comment */"
        self.assertEqual(string_conv, TestBundler.js_comments_endline2block(string))

    def test_endline_comment2(self):
        string = "var i = 1; // i am a comment"
        string_conv = "var i = 1; /* i am a comment */"
        self.assertEqual(string_conv, TestBundler.js_comments_endline2block(string))

    def test_endline_comment3(self):
        string = "var i = 1; // i am // just a comment"
        string_conv = "var i = 1; /* i am // just a comment */"
        self.assertEqual(string_conv, TestBundler.js_comments_endline2block(string))

    def test_endline_comment_multimixed(self):
        string = "var i1 = 1, // i am a comment\n" \
                 " i2=2; // that should be conv"
        string_conv = "var i1 = 1, /* i am a comment */\n" \
                      " i2=2; /* that should be conv */"
        self.assertEqual(string_conv, TestBundler.js_comments_endline2block(string))

