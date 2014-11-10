""" unit test for Bundler.strip_marked_line_from_css_or_js """


import unittest


from bundler import Bundler


class Test_strip_marked_line_from_css_or_js(unittest.TestCase):

    __stripIndicators = ["@sTrIp", "@remove", "@KILL"]

    @classmethod
    def strip(cls, string):
        return Bundler.strip_marked_line_from_css_or_js(string, cls.__stripIndicators)

    def test_none(self):
        string = "nothing to change here"
        self.assertEqual(string, self.strip(string))

    def test_not_in_word(self):
        string = "some" + self.__stripIndicators[0] + "thing"
        self.assertEqual(string, self.strip(string))

    def test_full(self):
        string = self.__stripIndicators[1]
        self.assertEqual("", self.strip(string))

    def test_full_cases(self):
        string = self.__stripIndicators[0]
        self.assertEqual("", self.strip(string))
        string = self.__stripIndicators[1].upper()
        self.assertEqual("", self.strip(string))
        string = self.__stripIndicators[2].lower()
        self.assertEqual("", self.strip(string))


    def test_single_js(self):
        string = "this should be empty // " + self.__stripIndicators[0]
        self.assertEqual("", self.strip(string))

    def test_single_css(self):
        string = "this should be empty /* " + self.__stripIndicators[1] + " */"
        self.assertEqual("", self.strip(string))

    def test_multi_1(self):
        do_not_strip = "do not strip"
        string = "remove me " + self.__stripIndicators[1] + "\n" + \
                 do_not_strip + "\n" \
                 "remove me too " + self.__stripIndicators[0]
        self.assertEqual(do_not_strip, self.strip(string))

    def test_multi_2(self):
        do_not_strip = ["do not strip", "do not strip"]

        string = "remove me " + self.__stripIndicators[1] + "\n" + \
                 do_not_strip[0] + "\n" \
                 "remove me too " + self.__stripIndicators[0] + "\n" + \
                 do_not_strip[1]
        self.assertEqual("\n".join(do_not_strip), self.strip(string))

