
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


class Bundler:

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
    def strip_tag_from_bs4(bs4doc, tagname):
        for node in bs4doc.find_all(tagname):
            node.extract()
        return bs4doc

    @staticmethod
    def strip_marked_line_from_css_or_js(string_css_or_js, marker):
        marker_re = re.compile("^.*" + marker + ".*$", flags=re.IGNORECASE)
        string_css_or_js = re.sub(marker_re, "", string_css_or_js, flags=re.MULTILINE)
        return string_css_or_js

    @staticmethod
    def src_is_external(uri):
        return uri.find("(.*:)?//") > -1

    @staticmethod
    def __preserve_html_entities(string):
        # FIXME preserve suspicious
        string = re.sub(r"&([a-zA-Z0-9#]+?);", r"~pe{\1}~", string)
        return string

    @staticmethod
    def __revert_html_entities(string):
        # FIXME TODO revert reserved suspicious
        string = re.sub(r"~pe\{([a-zA-Z0-9#]+?)\}~", r"&\1;", string)
        return string

    @staticmethod
    def compress_html(string, maxlen):
        re_whitespace = re.compile("[ \t\n\r]+")

        string_part_clean = ""
        string_parts_clean = []

        for string_part_raw in string:
            string_part_raw = re.sub(re_whitespace, " ", string_part_raw).strip()
            if len(string_part_clean) + len(string_part_raw) > maxlen:
                string_parts_clean.append(string_part_clean)
                string_part_clean = string_part_raw
            else:
                string_part_clean += string_part_raw
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
    def yui_compress(cls, kind, string, encoding="utf-8"):
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
    def fetch_external_js(cls, bs4doc, path):
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

    ### constants ###

    YUIC_TYPE_JS = "js"
    YUIC_TYPE_CSS = "css"

    FLAG_STRIP_COMMENTS = 1
    FLAG_STRIP_ON_BUILD = 2
    FLAG_COMPRESS = 4

    ### config ###

    __tag_stripOnBundle = 'striponbundle'
    __inline_stripOnBundle = "@striponbundle"

    __yuic = "yuicompressor-2.4.8.jar"

    ### instance variables ###

    _string = ""
    _path = ""
    _maxlen = 0
    _flags = 0

    ### instance methods ###

    def __init__(self, string, path=False, flags=0, maxlen=120):
        self._string = string
        self._path = path
        self._flags = flags
        self._maxlen = maxlen

    def __str__(self):
        string = self._string
        string = self.__preserve_html_entities(string)

        bs4doc = bs4.BeautifulSoup(string)
        del string

        self.strip_tag_from_bs4(bs4doc, self.__tag_stripOnBundle)

        self.fetch_external_js(bs4doc, self._path)
        for script in bs4doc.find_all('script', {'src': False}):
            # TODO yuic
            script.string = self.strip_comments_from_js(script.string)

        self.fetch_external_css(bs4doc, self._path)
        for style in bs4doc.find_all('style'):
            # TODO yuic
            style.string = self.strip_comments_from_css(style.string)

        self.strip_comments_from_bs4(bs4doc)

        string = bs4doc.prettify()  # alternative: str(bs4doc)
        del bs4doc

        string = self.__revert_html_entities(string)

        string = self.compress_html(string, self._maxlen)

        return string
