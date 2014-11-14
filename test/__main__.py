"""
run this from main dir: python -m test
"""

import unittest


# import the tests
from .compress_html import *
from .get_base_absolute import *
from .preserve_html_entities import *
from .src_is_external import *
from .strip_comments import *
from .strip_marked_line_from_css_or_js import *
from .check_flag import *
from .js_comments_endline2block import *
from .add_trailing_semicolon_to_js import *


# run the tests
if __name__ == '__main__':
     unittest.main()