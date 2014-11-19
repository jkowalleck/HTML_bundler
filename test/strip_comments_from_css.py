""" unit test for Bundler.strip_comments_from_css. """

import unittest

from bundler import Bundler


class Test_strip_comments_from_css(unittest.TestCase):
    code = "some code;"

    comment_block = "/* some block comment */"
    comment_block_multiline = "/* some \n multi line \n block comment */"

    flags_default = Bundler.FLAG_STRIP_COMMENTS_CSS

    def test_none(self):
        string = self.code
        string_stripped = string
        self.assertEqual(string_stripped, Bundler.strip_comments_from_css(string, self.flags_default))

    def test_suspicious_complex(self):
        string = self.code + '"suspect ' + self.comment_block + '";'
        string_stripped = self.code + '"suspect ' + self.comment_block + '";'
        self.assertEqual(string_stripped, Bundler.strip_comments_from_css(string, self.flags_default))

    def test_block_only(self):
        string = self.comment_block
        string_stripped = ""
        self.assertEqual(string_stripped, Bundler.strip_comments_from_css(string, self.flags_default))

    def test_block_ending(self):
        string = self.code + self.comment_block
        string_stripped = self.code
        self.assertEqual(string_stripped, Bundler.strip_comments_from_css(string, self.flags_default))

    def test_block_beginning(self):
        string = self.comment_block + self.code
        string_stripped = self.code
        self.assertEqual(string_stripped, Bundler.strip_comments_from_css(string, self.flags_default))

    def test_block_middle(self):
        string = self.code + self.comment_block + self.code
        string_stripped = self.code + self.code
        self.assertEqual(string_stripped, Bundler.strip_comments_from_css(string, self.flags_default))

    def test_block_middle_multiple(self):
        string = self.code + self.comment_block + self.code + self.comment_block + self.code
        string_stripped = self.code + self.code + self.code
        self.assertEqual(string_stripped, Bundler.strip_comments_from_css(string, self.flags_default))

    def test_block_middle_multiline(self):
        string = self.code + "\n" + self.code + self.comment_block_multiline + self.code
        string_stripped = self.code + "\n" + self.code + self.code
        self.assertEqual(string_stripped, Bundler.strip_comments_from_css(string, self.flags_default))

    def test_keep_first_singleline(self):
        string = self.comment_block + "\n" + self.code + self.comment_block_multiline + self.code
        string_stripped = self.comment_block + "\n" + self.code + self.code
        flags = self.flags_default | Bundler.FLAG_STRIP_COMMENTS_CSS_KEEP_FIRST
        self.assertEqual(string_stripped, Bundler.strip_comments_from_css(string, flags))

    def test_keep_first_multiline(self):
        string = self.comment_block_multiline + "\n" + self.code + self.comment_block_multiline + self.code
        string_stripped = self.comment_block_multiline + "\n" + self.code + self.code
        flags = self.flags_default | Bundler.FLAG_STRIP_COMMENTS_CSS_KEEP_FIRST
        self.assertEqual(string_stripped, Bundler.strip_comments_from_css(string, flags))



if __name__ == '__main__':
    unittest.main()