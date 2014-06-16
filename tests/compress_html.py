#!/usr/bin/env python

""" unit test for Bundler.strip_comments_from_... """

import unittest

import random

from bundler import Bundler


class Test(unittest.TestCase):
    string = """
        <html><head>
                <title>some title</title>
            </head><body>
                <textare>
                    some text
                    that is
                    a bit
                    longer
                    than needed and is split over
                    multiple lines.

                    so a cleanup
                    might be needed.
                </textarea>
            </body></html>
        """

    def test_eq0(self):
        compressed = "" \
            "<html><head>\n" \
            "<title>some title</title>\n" \
            "</head><body>\n" \
            "<textare>\n" \
            "some text\n" \
            "that is\n" \
            "a bit\n" \
            "longer\n" \
            "than needed and is split over\n" \
            "multiple lines.\n" \
            "so a cleanup\n" \
            "might be needed.\n" \
            "</textarea>\n" \
            "</body></html>"
        self.assertEqual(Bundler.compress_html(self.string, 0), compressed)

    def test_lt0(self):
        compressed = "" \
            "<html><head><title>some title</title></head><body><textare>some text that is a bit longer than " \
            "needed and is split over multiple lines. so a cleanup might be needed.</textarea></body></html>"
        self.assertEqual(Bundler.compress_html(self.string, -1), compressed)

    def test_30(self):
        compressed = "" \
            "<html><head>\n" \
            "<title>some title</title>\n" \
            "</head><body><textare>\n" \
            "some text that is a bit longer\n" \
            "than needed and is split over\n" \
            "multiple lines. so a cleanup\n" \
            "might be needed.</textarea>\n" \
            "</body></html>"
        self.assertEqual(Bundler.compress_html(self.string, 30), compressed)

    def test_50(self):
        compressed = "" \
            "<html><head><title>some title</title></head><body>\n" \
            "<textare>some text that is a bit longer\n" \
            "than needed and is split over multiple lines.\n" \
            "so a cleanup might be needed.</textarea>\n" \
            "</body></html>"
        self.assertEqual(Bundler.compress_html(self.string, 50), compressed)

if __name__ == '__main__':
    unittest.main()