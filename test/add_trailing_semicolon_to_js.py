""" test Bundler._add_trailing_semicolon_to_js """

import unittest

from bundler import Bundler


### class inherited for access to protected funcs


class TestBundler(Bundler):

    @classmethod
    def add_trailing_semicolon_to_js(cls, string):
        return cls._add_trailing_semicolon_to_js(string)


### test

class Test_add_trailing_semicolon_to_js(unittest.TestCase):

    def test_empty(self):
        string = ""
        self.assertEqual(string, TestBundler.add_trailing_semicolon_to_js(string))

    def test_def(self):
        string = "var a = 1"
        string_conv = "var a = 1;"
        self.assertEqual(string_conv, TestBundler.add_trailing_semicolon_to_js(string))

    def test_def_multiline(self):
        string = "var v1 , v2 , \n" \
                 "v3 ,  \n" \
                 "v4"
        string_conv = "var v1 , v2 , \n" \
                      "v3 ,  \n" \
                      "v4;"
        self.assertEqual(string_conv, TestBundler.add_trailing_semicolon_to_js(string))

    def test_def_object(self):
        string = "var obj = { x : {}" \
                 "\n}"
        string_conv = "var obj = { x : {}" \
                      "\n};"
        self.assertEqual(string_conv, TestBundler.add_trailing_semicolon_to_js(string))

    def test_width_clockcomment(self):
        string = "var a = 1 /* a comment */"
        string_conv = "var a = 1; /* a comment */"
        self.assertEqual(string_conv, TestBundler.add_trailing_semicolon_to_js(string))

    def test_width_clockcomment_multiple (self):
        string = "var a = 1 /* a */ /* multiple */ /* comments */"
        string_conv = "var a = 1; /* a */ /* multiple */ /* comments */"
        self.assertEqual(string_conv, TestBundler.add_trailing_semicolon_to_js(string))

    def test_width_linecomment(self):
        string = "var a = 1 // a comment"
        string_conv = "var a = 1; // a comment"
        self.assertEqual(string_conv, TestBundler.add_trailing_semicolon_to_js(string))

    def test_width_comments(self):
        string = "var a = 1 /* a */ // comment"
        string_conv = "var a = 1; /* a */ // comment"
        self.assertEqual(string_conv, TestBundler.add_trailing_semicolon_to_js(string))

    def test_call(self):
        string = "var a = f()"
        string_conv = "var a = f();"
        self.assertEqual(string_conv, TestBundler.add_trailing_semicolon_to_js(string))

    def test_if(self):
        string = "if ( false )  \n" \
                 " f()"
        string_conv = "if ( false )  \n" \
                      " f();"
        self.assertEqual(string_conv, TestBundler.add_trailing_semicolon_to_js(string))

    def test_switch(self):
        string = "switch ( false )  \n" \
                 " { }"
        self.assertEqual(string, TestBundler.add_trailing_semicolon_to_js(string))

    def test_while(self):
        string = "while ( false )  \n" \
                 " f()"
        string_conv = "while ( false )  \n" \
                      " f();"
        self.assertEqual(string_conv, TestBundler.add_trailing_semicolon_to_js(string))

    def test_do(self):
        string = "do {  \n" \
                 "} while ( false )"
        self.assertEqual(string, TestBundler.add_trailing_semicolon_to_js(string))

    def test_for(self):
        string = "for ( var i=0 ; i<1 ; ++0 ) \n" \
                 "{  \n" \
                 "}"
        self.assertEqual(string, TestBundler.add_trailing_semicolon_to_js(string))

    def test_function(self):
        string = "function  ( ) \n" \
                 "{  \n" \
                 "}"
        self.assertEqual(string, TestBundler.add_trailing_semicolon_to_js(string))

    def test_try(self):
        string = "try {}  \n" \
                 "catch () \n" \
                 "{}"
        self.assertEqual(string, TestBundler.add_trailing_semicolon_to_js(string))

    def test_with(self):
            string = "with { obj }  \n" \
                     "{}"
            self.assertEqual(string, TestBundler.add_trailing_semicolon_to_js(string))

    def rest_lambda(self):
        string = "(function () { return true})('foo',bar)\n" \
                 "function(){return true;}('foo')\n" \
                 "!function(){}()\n" \
                 "(function(){}())\n" \
                 "var f = function () {}"
        string_conv= "(function () { return true})('foo',bar);\n" \
                     "function(){return true;}('foo');\n" \
                     "!function(){foo}();\n" \
                     "(function(){}());\n" \
                     "var f = function () {};"
        self.assertEqual(string_conv, TestBundler.add_trailing_semicolon_to_js(string))