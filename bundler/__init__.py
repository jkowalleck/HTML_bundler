
__author__ = "Jan Kowalleck (jan.kowalleck@googlemail.com)"
__copyright__ = "Copyright (c) 2014 Jan Kowalleck"
__license__ = "MIT"

__all__ = ['Bundler']


### some imports ####
import sys
import os
import re
import chardet
import subprocess

import bs4

from lib import jsstrip


### the builder -here we go ###


class Bundler(object):

    ### constants ###

    YUIC_TYPE_JS = "js"
    YUIC_TYPE_CSS = "css"

    FLAG_STRIP_COMMENTS_HTML = 1
    FLAG_STRIP_COMMENTS_JS_BLOCK = 2
    FLAG_STRIP_COMMENTS_JS_ENDLINE = 4
    FLAG_STRIP_COMMENTS_JS_KEEP_FIRST = 8
    FLAG_STRIP_COMMENTS_CSS = 16
    FLAG_STRIP_COMMENTS_CSS_KEEP_FIRST = 32
    FLAG_STRIP_COMMENTS_JS = FLAG_STRIP_COMMENTS_JS_BLOCK | FLAG_STRIP_COMMENTS_JS_ENDLINE
    FLAG_STRIP_COMMENTS = FLAG_STRIP_COMMENTS_HTML | FLAG_STRIP_COMMENTS_JS | FLAG_STRIP_COMMENTS_CSS
    FLAG_STRIP_COMMENTS_KEEP_FIRST = FLAG_STRIP_COMMENTS_JS_KEEP_FIRST | FLAG_STRIP_COMMENTS_CSS_KEEP_FIRST

    FLAG_OPTIMIZE_JS = 64
    FLAG_OPTIMIZE_CSS = 128
    FLAG_OPTIMIZE = FLAG_OPTIMIZE_CSS | FLAG_OPTIMIZE_JS

    FLAG_COMPRESS = 256

    ### static methods ###

    @staticmethod
    def _strip_comments_from_js_or_css(string, optSaveFirst=False, optWhite=False, optSingle=True, optMulti=True):
        string = jsstrip.strip(string,
                               optSaveFirst=optSaveFirst, optWhite=optWhite, optSingle=optSingle, optMulti=optMulti)
        string = "\n".join([line for line in string.split("\n") if len(line.strip()) > 0])  # strip empty lines
        return string

    @staticmethod
    def strip_comments_from_bs4(bs4doc):
        for comment in bs4doc.find_all(text=lambda text: isinstance(text, bs4.Comment)):
            comment.extract()
        return bs4doc

    @staticmethod
    def strip_tag_from_bs4(bs4doc, tagnames):
        for tagname in [tagname.strip() for tagname in tagnames]:
            if len(tagname) > 0:
                for node in bs4doc.find_all(tagname, recursive=True):
                    node.extract()
        return bs4doc

    @staticmethod
    def strip_marked_line_from_css_or_js(string_css_or_js, markers):
        for marker in markers:
            marker = marker.strip()
            if len(markers) > 0:
                marker_re = re.compile("^(?:.*\s)?" + re.escape(marker) + "(?:\s.*)?$", flags=re.IGNORECASE|re.MULTILINE)
                string_css_or_js = re.sub(marker_re, "", string_css_or_js)
        return string_css_or_js

    @staticmethod
    def src_is_external(uri):
        # read http://en.wikipedia.org/wiki/URI_scheme
        match = re.match(r"^(?:[a-z][a-z0-9\+\.\-]+?:)?//", uri, flags=re.IGNORECASE)
        return match

    @staticmethod
    def _preserve_html_entities(string):
        string = re.sub(r"~pe\{(.+?)\}~", r"~pe{!\1}~", string)
        string = re.sub(r"&(#[:digit:]+?|#x[:xdigit:]+?|[:alnum:]+?);", r"~pe{\1}~", string)
        return string

    @staticmethod
    def _revert_html_entities(string):
        string = re.sub(r"~pe\{(#[:digit:]+?|#x[:xdigit:]+?|[:alnum:]+?)\}~", r"&\1;", string)
        string = re.sub(r"~pe\{!(.+?)\}~", r"~pe{\1}~", string)
        return string

    @staticmethod
    def compress_html(string, length):
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
            if length < 0 or len(string_part_clean) + len(string_part_raw) <= length:
                if string_part_clean and string_part_raw \
                        and string_part_clean[-1] != ">" and string_part_raw[0] != "<":
                    string_part_raw = " " + string_part_raw
                string_part_clean += string_part_raw
            else:
                if string_part_clean:
                    string_parts_clean.append(string_part_clean)
                string_part_clean = string_part_raw

        string_parts_clean.append(string_part_clean)

        return "\n".join(str(part) for part in string_parts_clean)

    ### factory methods ###

    @classmethod
    def from_file(cls, filePath, flags):
        if not os.path.isfile(filePath):
            raise Exception()

        path = os.path.dirname(filePath)

        fh = open(filePath, 'r')
        string = fh.read()
        fh.close()
        del fh

        return cls(string, path, flags)

    ### class methods ###

    @classmethod
    def strip_comments_from_js(cls, string, flags=FLAG_STRIP_COMMENTS_JS):
        optSaveFirst = (flags & cls.FLAG_STRIP_COMMENTS_JS_KEEP_FIRST != 0)
        optMulti = (flags & cls.FLAG_STRIP_COMMENTS_JS_BLOCK != 0)
        optSingle = (flags & cls.FLAG_STRIP_COMMENTS_JS_ENDLINE != 0)
        if optMulti or optSingle:
            string = cls._strip_comments_from_js_or_css(string, optWhite=False,
                                                        optSaveFirst=optSaveFirst,
                                                        optSingle=optSingle, optMulti=optMulti)
        return string

    @classmethod
    def strip_comments_from_css(cls, string, flags=FLAG_STRIP_COMMENTS_CSS):
        optSaveFirst = (flags & cls.FLAG_STRIP_COMMENTS_CSS_KEEP_FIRST != 0)
        optMulti = (flags & cls.FLAG_STRIP_COMMENTS_CSS != 0)
        if optMulti:
            string = cls._strip_comments_from_js_or_css(string, optWhite=False, optSingle=False,
                                                        optSaveFirst=optSaveFirst,
                                                        optMulti=optMulti)
        return string

    @classmethod
    def yui_compress(cls, kind, string, flags=0):
        # TODO use flags
        process = subprocess.Popen(
            ["java",
                "-jar", cls.__yuic,
                "--line-break", "0",
                "--type", kind,
                "--charset", chardet.detect(string)['encoding']
            ],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=os.path.dirname(os.path.realpath(__file__)))

        stdout, stderr = process.communicate(string.encode())
        process.terminate()

        success = stderr == b""
        return success, (stdout if success else stderr).decode(sys.stdout.encoding)

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

    __yuic = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "lib", "yuicompressor-2.4.8.jar")

    ### instance variables ###

    strip_tags = []
    strip_inline_js = []
    strip_inline_css = []

    string = ""
    path = ""
    htroot = ""
    compress_len = 0
    flags = 0

    ### instance methods ###

    def __init__(self, string, path="", htroot="",
                 flags=FLAG_STRIP_COMMENTS | FLAG_COMPRESS,
                 compress_len=120, encoding="utf-8",
                 strip_tags='stripOnBundle',
                 strip_inline_js="@stripOnBundle",
                 strip_inline_css="@stripOnBundle"):

        # param 'encoding' is currently not used

        self.string = string
        self.path = path
        self.htroot = htroot
        self.flags = flags
        self.compress_len = compress_len
        self.strip_tags = strip_tags.split(",")
        self.strip_inline_js = strip_inline_js.split(",")
        self.strip_inline_css = strip_inline_css.split(",")

    def bundle(self):
        string = self.string
        string = self._preserve_html_entities(string)

        bs4doc = bs4.BeautifulSoup(string)
        del string

        if self.strip_tags:
            self.strip_tag_from_bs4(bs4doc, self.strip_tags)

        self.fetch_external_js(bs4doc, self.path)
        for script in bs4doc.find_all('script', {'src': False}):
            script_string = script.string
            if self.strip_inline_js:
                script_string = self.strip_marked_line_from_css_or_js(script_string, self.strip_inline_js)
            script_string = self.strip_comments_from_js(script_string, flags=self.flags)
            if self.flags & self.FLAG_OPTIMIZE_JS != 0:
                script_string = self.yui_compress(self.YUIC_TYPE_JS, script_string, flags=self.flags)
            script.string = script_string
            del script_string

        self.fetch_external_css(bs4doc, self.path)
        for style in bs4doc.find_all('style'):
            style_string = style.string
            if self.strip_inline_css:
                style_string = self.strip_marked_line_from_css_or_js(style_string, self.strip_inline_css)
            style_string = self.strip_comments_from_css(style_string, flags=self.flags)
            if self.flags & self.FLAG_OPTIMIZE_CSS != 0:
                style_string = self.yui_compress(self.YUIC_TYPE_CSS, style_string, flags=self.flags)
            style.string = style_string
            del style_string

        if self.flags & self.FLAG_STRIP_COMMENTS_HTML == self.FLAG_STRIP_COMMENTS_HTML:
            self.strip_comments_from_bs4(bs4doc)

        string = bs4doc.prettify()
        del bs4doc

        string = self._revert_html_entities(string)

        if self.flags & self.FLAG_COMPRESS == self.FLAG_COMPRESS:
            string = self.compress_html(string, self.compress_len)

        return string

    def __str__(self):
        return self.bundle()
