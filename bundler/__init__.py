
__author__ = "Jan Kowalleck (jan.kowalleck@googlemail.com)"
__copyright__ = "Copyright (c) 2014 Jan Kowalleck"
__license__ = "MIT"

__all__ = ['Bundler', 'BundlerPathIsNoDirException']


### some imports ####
#import sys
import os
import re
#import chardet
#import subprocess

import bs4

from jslex import JsLexer

from lib import jsstrip


### the builder -here we go ###


class Bundler(object):

    ### constants ###

    FLAG_STRIP_COMMENTS_HTML = 1
    FLAG_STRIP_COMMENTS_JS_BLOCK = 2
    FLAG_STRIP_COMMENTS_JS_ENDLINE = 4
    FLAG_STRIP_COMMENTS_JS_KEEP_FIRST = 8
    FLAG_STRIP_COMMENTS_CSS = 16
    FLAG_STRIP_COMMENTS_CSS_KEEP_FIRST = 32
    FLAG_STRIP_COMMENTS_JS = FLAG_STRIP_COMMENTS_JS_BLOCK | FLAG_STRIP_COMMENTS_JS_ENDLINE
    FLAG_STRIP_COMMENTS = FLAG_STRIP_COMMENTS_HTML | FLAG_STRIP_COMMENTS_JS | FLAG_STRIP_COMMENTS_CSS
    FLAG_STRIP_COMMENTS_KEEP_FIRST = FLAG_STRIP_COMMENTS_JS_KEEP_FIRST | FLAG_STRIP_COMMENTS_CSS_KEEP_FIRST

    FLAG_COMPRESS = 256

    ### static methods ###

    @staticmethod
    def _check_flag(target, flag):
        return target & flag == flag

    @staticmethod
    def _strip_comments_from_js_or_css(string, optSaveFirst=False, optWhite=False, optSingle=True, optMulti=True):
        string = jsstrip.strip(string,
                               optSaveFirst=optSaveFirst, optWhite=optWhite, optSingle=optSingle, optMulti=optMulti)
        string = "\n".join([line for line in string.splitlines() if len(line.strip()) > 0])  # strip empty lines
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
                tagname = tagname.lower()
                for node in bs4doc.find_all(tagname, recursive=True):
                    node.extract()
        return bs4doc

    @staticmethod
    def strip_marked_line_from_css_or_js(string_css_or_js, markers):
        markers = [re.escape(marker) for marker in [marker.strip() for marker in markers] if len(marker) > 0]
        if len(markers) > 0:
            marker_re = re.compile("^(?:.*\s)?(?:" + "|".join(markers) + ")(?:\s.*)?$",  flags=re.IGNORECASE)
            lines = []
            for line in string_css_or_js.splitlines():
                if not marker_re.match(line):
                    lines.append(line)
            string_css_or_js = "\n".join(lines)
        return string_css_or_js

    @staticmethod
    def src_is_external(uri):
        # read http://en.wikipedia.org/wiki/URI_scheme
        match = re.match(r'^(?:[a-z][a-z0-9\+\.\-]+?:)?//', uri)
        return match

    @staticmethod
    def _preserve_html_entities(string):
        string = re.sub(r'~pe\{(.+?)\}~', r'~pe{!\1}~', string)
        string = re.sub(r'&(#[0-9]+?|#x[0-9A-Fa-f]+?|[0-9A-Za-z]+?);', r'~pe{\1}~', string)
        return string

    @staticmethod
    def _revert_html_entities(string):
        string = re.sub(r'~pe\{(#[0-9]+?|#x[0-9A-Fa-f]+?|[0-9A-Za-z]+?)\}~', r'&\1;', string)
        string = re.sub(r'~pe\{!(.+?)\}~', r'~pe{\1}~', string)
        return string

    @staticmethod
    def compress_html(string, length):
        """
            minlen == 0 : everything in a new line
            minlen < 0 : all in one line
        """

        re_whitespace = re.compile("[ \t\n\r]+")

        string_part_clean = ""
        string_parts_clean = []

        for string_part_raw in string.splitlines():
            string_part_raw = re.sub(re_whitespace, " ", string_part_raw).strip()
            if len(string_part_raw) == 0:
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

        return "\n".join(part for part in string_parts_clean)

    ### factory methods ###

    @classmethod
    def from_file(cls, filePath, flags):
        """ untested """
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
    def _js_comments_endline2block(cls, string):
        return "".join([('/* ' + tok.strip(' \t\n\r/') + ' */' if name == 'linecomment' else tok)
                        for name, tok in JsLexer().lex(string)])

    @classmethod
    def strip_comments_from_js(cls, string, flags=FLAG_STRIP_COMMENTS_JS):
        optSaveFirst = cls._check_flag(flags, cls.FLAG_STRIP_COMMENTS_JS_KEEP_FIRST)
        optMulti = cls._check_flag(flags, cls.FLAG_STRIP_COMMENTS_JS_BLOCK)
        optSingle = cls._check_flag(flags, cls.FLAG_STRIP_COMMENTS_JS_ENDLINE)
        if optMulti or optSingle:
            string = cls._strip_comments_from_js_or_css(string, optWhite=False,
                                                        optSaveFirst=optSaveFirst,
                                                        optSingle=optSingle, optMulti=optMulti)
        return string

    @classmethod
    def strip_comments_from_css(cls, string, flags=FLAG_STRIP_COMMENTS_CSS):
        optSaveFirst = cls._check_flag(flags, cls.FLAG_STRIP_COMMENTS_CSS_KEEP_FIRST)
        optMulti = cls._check_flag(flags, cls.FLAG_STRIP_COMMENTS_CSS)
        if optMulti:
            string = cls._strip_comments_from_js_or_css(string, optWhite=False, optSingle=False,
                                                        optSaveFirst=optSaveFirst,
                                                        optMulti=optMulti)
        return string

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

    ### instance variables ###

    strip_tags = []
    strip_inline_js = []
    strip_inline_css = []

    string = ""
    encoding = ""
    path = ""
    htroot = ""
    compress_len = 0
    flags = 0

    ### instance methods ###

    def __init__(self, string, path="", htroot="",
                 flags=FLAG_STRIP_COMMENTS | FLAG_COMPRESS,
                 compress_len=120, encoding="utf-8",
                 strip_tags=["stripOnBundle"],
                 strip_inline_js=["@stripOnBundle"],
                 strip_inline_css=["@stripOnBundle"]):
        self.encoding = encoding
        self.string = string
        self.path = (os.path.abspath(path) if path else os.getcwd())
        self.htroot = (os.path.abspath(htroot) if htroot else path)
        self.flags = max(flags, 0)
        self.compress_len = max(compress_len, 0)
        self.strip_tags = strip_tags
        self.strip_inline_js = strip_inline_js
        self.strip_inline_css = strip_inline_css
        if not os.path.isdir(self.path):
            raise BundlerPathIsNoDirException(self.path)
        if not os.path.isdir(self.htroot):
            raise BundlerPathIsNoDirException(self.htroot)

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
            if len(self.strip_inline_js) > 0:
                script_string = self.strip_marked_line_from_css_or_js(script_string, self.strip_inline_js)
            script_string = self.strip_comments_from_js(script_string, flags=self.flags)
            script.string = script_string
            del script_string

        for script in bs4doc.find_all('script'):
            script.string = self._js_comments_endline2block(script.string)

        self.fetch_external_css(bs4doc, self.path)
        for style in bs4doc.find_all('style'):
            style_string = style.string
            if len(self.strip_inline_css) > 0:
                style_string = self.strip_marked_line_from_css_or_js(style_string, self.strip_inline_css)
            style_string = self.strip_comments_from_css(style_string, flags=self.flags)
            style.string = style_string
            del style_string

        if self._check_flag(self.flags, self.FLAG_STRIP_COMMENTS_HTML):
            self.strip_comments_from_bs4(bs4doc)

        string = bs4doc.prettify()
        del bs4doc

        string = self._revert_html_entities(string)

        if self._check_flag(self.flags, self.FLAG_COMPRESS):
            string = self.compress_html(string, self.compress_len)

        if hasattr(string, 'encode'):
            string = string.encode(self.encoding)

        return string

    def __str__(self):
        return self.bundle()


class BundlerPathIsNoDirException(Exception):
    pass