
__author__ = "Jan Kowalleck (jan.kowalleck@googlemail.com)"
__copyright__ = "Copyright (c) 2014 Jan Kowalleck"
__license__ = "MIT"

__all__ = ['Bundler']


import sys
import os
import re
import subprocess

import bs4
import html5lib   # used by BeautifulSoup


class Bundler(object):

    ### constants ###

    YUIC_TYPE_JS = "js"
    YUIC_TYPE_CSS = "css"

    FLAG_STRIP_COMMENTS = 1
    FLAG_STRIP_ON_BUILD = 2
    FLAG_COMPRESS = 4

    ### static methods ###

    @staticmethod
    def _strip_comments_block(string_css_or_js):
        while True:
            string_css_or_js, replaced = re.subn(r"/\*.*?\*/", "", string_css_or_js, flags=re.DOTALL)  # strip block
            if replaced < 1:
                return string_css_or_js

    @staticmethod
    def _strip_comments_inline(string_js):
        string_js = re.sub(r"//.*$", "", string_js, flags=re.MULTILINE)  # strip end line
        return string_js

    @staticmethod
    def strip_comments_from_bs4(bs4doc):
        for comment in bs4doc.find_all(text=lambda text: isinstance(text, bs4.Comment)):
            comment.extract()
        return bs4doc

    @staticmethod
    def strip_tag_from_bs4(bs4doc, tagnames):
        for tagname in tagnames:
            for node in bs4doc.find_all(tagname):
                node.extract()
        return bs4doc

    @staticmethod
    def strip_marked_line_from_css_or_js(string_css_or_js, markers):
        markers = [re.escape(marker) for marker in markers]
        marker_re = re.compile("^.*(" + "|".join(markers) + ").*$", flags=re.IGNORECASE)
        string_css_or_js = re.sub(marker_re, "", string_css_or_js, flags=re.MULTILINE)
        return string_css_or_js

    @staticmethod
    def src_is_external(uri):
        return uri.find("(.*:)?//") > -1

    @staticmethod
    def __preserve_html_entities(string):
        # FIXME preserve suspicious
        string = re.sub(r"&([a-zA-Z0-9#]+?);", r"~pe{\1}~", str(string))
        return string

    @staticmethod
    def __revert_html_entities(string):
        # FIXME TODO revert reserved suspicious
        string = re.sub(r"~pe\{([a-zA-Z0-9#]+?)\}~", r"&\1;", str(string))
        return string

    @staticmethod
    def compress_html(string, len):
        """
            minlen == 0 : everything in a new line
            minlen < 0 : all in one line
        """

        string = str(string)

        re_whitespace = re.compile("[ \t\n\r]+")

        string_part_clean = ""
        string_parts_clean = []

        for string_part_raw in string.split("\n"):
            string_part_raw = re.sub(re_whitespace, " ", string_part_raw).strip()
            if not string_part_raw:
                continue
            if len < 0 or len(string_part_clean) + len(string_part_raw) <= len:
                if string_part_clean and string_part_raw and string_part_clean[-1] != ">" and string_part_raw[0] != "<":
                    string_part_raw = " " + string_part_raw
                string_part_clean += string_part_raw
            else:
                if string_part_clean:
                    string_parts_clean.append(string_part_clean)
                string_part_clean = string_part_raw

        string_parts_clean.append(string_part_clean)

        return "\n".join(str(part) for part in string_parts_clean)

    ### class methods ###

    @classmethod
    def from_file(cls, file, flags):
        if not os.path.isfile(file):
            raise Exception()

        path = os.path.dirname(file)

        fh = open(file, 'r')
        string = fh.read()
        fh.close()
        del fh

        return cls(string, path, flags)

    @classmethod
    def yui_compress(cls, kind, string, encoding="utf-8", flags=0):
        # TODO use flags
        process = subprocess.Popen(
            ["java",
                "-jar", cls.__yuic,
                "--line-break", "0",
                "--type", kind,
                "--charset", encoding
            ],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=os.path.dirname(os.path.realpath(__file__)))

        stdout, stderr = process.communicate(string.encode())
        process.terminate()

        success = stderr == b""
        return success, (stdout if success else stderr).decode(sys.stdout.encoding)

    @classmethod
    def strip_comments_from_css(cls, string_css):
        string_css = cls._strip_comments_block(string_css)
        return string_css

    @classmethod
    def strip_comments_from_js(cls, string_js):
        string_js = cls._strip_comments_block(string_js)
        string_js = cls._strip_comments_inline(string_js)
        return string_js

    @classmethod
    def get_base_absolute(cls, bs4doc, path_file, path_base=""):
        path = path_file
        """
        not implemented, since i don't use it, yet

        idea :
         $base = bs4doc.find('head').find('base')['href']
         if cls.src_is_external($base): return FALSE

         $base = os.path.join(path, $base) # breaks on /

         if not isdir($base): return FALSE

         return $base
        """
        # FIXME build a function body that works
        return path

    @classmethod
    def fetch_external_js(cls, bs4doc, path):
        path = cls.get_base_absolute(bs4doc, path)
        if path:
            for script in bs4doc.find_all('script', {'src': True}):
                src = script['src']
                if cls.src_is_external(src):
                    continue

                src_path = os.path.join(path, src)
                if not os.path.isfile(src_path):
                    # script.extract()
                    continue

                del script['src']
                fh = open(src_path, "r")
                script.string = fh.read()
                fh.close()
                del fh

        return bs4doc

    @classmethod
    def fetch_external_css(cls, bs4doc, path):
        path = cls.get_base_absolute(bs4doc, path)
        if path:
            for link in bs4doc.find_all('link', {'rel': 'stylesheet', 'href': True}):
                src = link['href']
                if cls.src_is_external(src):
                    continue

                src_path = os.path.join(path, src)
                if not os.path.isfile(src_path):
                    # link.extract()
                    continue

                fh = open(src_path, "r")
                style_content = fh.read()
                fh.close()
                del fh

                style_inline = bs4doc.new_tag("style", type="text/css")
                style_inline.string = style_content
                link.replace_with(style_inline)

        return bs4doc

    ### config ###

    __yuic = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "bin", "yuicompressor-2.4.8.jar")

    ### instance variables ###

    stripOnBundle_tags = ['striponbundle']
    stripOnBundle_inline_js = ["@striponbundle"]
    stripOnBundle_inline_css = ["@striponbundle"]

    string = ""
    path = ""
    htroot = ""
    compress_len = 0
    flags = 0

    ### instance methods ###
    def __init__(self, string, path="", htroot="", flags=0, compress_len=120, encoding="utf-8"):
        self.string = string.encode(encoding)
        self.path = path
        self.htroot = htroot
        self.flags = flags
        self.compress_len = compress_len

    def bundle(self):
        string = self.string
        string = self.__preserve_html_entities(string)

        bs4doc = bs4.BeautifulSoup(string)
        del string

        self.strip_tag_from_bs4(bs4doc, self.stripOnBundle_tags)

        self.fetch_external_js(bs4doc, self.path)
        for script in bs4doc.find_all('script', {'src': False}):
            script_string = script.string
            script_string = self.strip_marked_line_from_css_or_js(script_string, self.stripOnBundle_inline_js)
            script_string = self.strip_comments_from_js(script_string)
            script_string = self.yui_compress(self.YUIC_TYPE_JS, script_string, flags=self.flags)
            script.string = script_string
            del script_string

        self.fetch_external_css(bs4doc, self.path)
        for style in bs4doc.find_all('style'):
            style_string = style.string
            style_string = self.strip_marked_line_from_css_or_js(style_string, self.stripOnBundle_inline_css)
            style_string = self.strip_comments_from_css(style_string)
            style_string = self.yui_compress(self.YUIC_TYPE_CSS, style_string, flags=self.flags)
            style.string = style_string
            del style_string

        self.strip_comments_from_bs4(bs4doc)

        string = bs4doc.prettify()  # alternative: str(bs4doc)
        del bs4doc

        string = self.__revert_html_entities(string)

        string = self.compress_html(string, self.compress_len)

        return string

    def __str__(self):
        return self.bundle()