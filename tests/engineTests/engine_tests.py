import unittest
import os
import engine.file_managers
from engine.file_managers import Tokens, VerbatimElement, LoopElement, ReplacementElement, BlankElement, EolElement


class VariableManagerTests(unittest.TestCase):
    """
    Unit tests for the class VariableManager
    """

    target_dict = {"variable1": "hello",
                   "array1": ["a", "b", "c"],
                   "variable2": "bye"}

    def test_parse_correct_line_string(self):
        """
        Test of the parsing method with correct entry when the value is a string.
        """
        try:
            token, value = engine.file_managers.VariableManager._parse_line('"token": "value"')
            self.assertEqual(token, 'token', 'It did not obtain the token expected')
            self.assertEqual(value, 'value', 'It did not obtain the value expected')
        except engine.file_managers.FileParseException:
            self.fail('Exception parsing the entry')

    def test_parse_correct_line_list(self):
        """
        Test of the parsing method with correct entry when the value is a list.
        """
        try:
            token, value = engine.file_managers.VariableManager._parse_line('"token": ["value1", "value2", "value3"]')
            self.assertEqual(token, 'token', 'It did not obtain the token expected')
            self.assertIsInstance(value, list, 'The value is not a list')
            self.assertListEqual(
                value, ["value1", "value2", "value3"], 'The list obtained is not equal to the original')
        except engine.file_managers.FileParseException:
            self.fail('Exception parsing the entry')

    def test_parse_incorrect_line_token_wrong(self):
        """
        Test of the parsing method with wrong entry when the token is wrong.
        """
        try:
            engine.file_managers.VariableManager._parse_line('"tok":en": "value"')
            self.fail('It should have failed but somehow it went through')
        except engine.file_managers.FileParseException:
            pass

    def test_parse_incorrect_line_string_value_wrong(self):
        """
        Test of the parsing method with a wrong entry when the value is a malformed string.
        """
        try:
            for l in ['"token": "val"ue"', '"token": val"ue"', '"token": val"ue']:
                engine.file_managers.VariableManager._parse_line(l)
                self.fail('It should have failed but somehow it went through with {}'.format(l))
        except engine.file_managers.FileParseException:
            pass

    def test_parse_incorrect_line_list_value_wrong(self):
        """
        Test of the parsing method with a wrong entry when the value is a list of malformed strings or a malformed
        list of correct strings or a malformed list of malformed strings.
        """
        try:
            for l in ['"token": ["val"ue"]', '"token": [val"ue"]', '"token": [val"ue]', '"token": val"ue]',
                      '"token": [val"ue']:
                engine.file_managers.VariableManager._parse_line(l)
                self.fail('It should have failed but somehow it went through with {}'.format(l))
        except engine.file_managers.FileParseException:
            pass

    def _test_parse_correct_file(self, filename):
        try:
            mgr = engine.file_managers.VariableManager(path_composer(filename))
            mgr.parse()
            self.assertTrue(VariableManagerTests.target_dict, mgr._variables)
        except IOError:
            self.fail('I could not find the file {}'.format(filename))
        except engine.file_managers.LineParseException as e:
            self.fail(e)

    def test_parse_correct_file(self):
        self._test_parse_correct_file('correct_var_file.txt')

    def test_parse_correct_file_duplicates(self):
        self._test_parse_correct_file('correct_var_file_duplicates.txt')

    def test_parse_correct_file_scrambled(self):
        self._test_parse_correct_file('correct_var_file_scrambled.txt')


def path_composer(filename):
    """
    Utility function that composes the path of a file in the test resources folder of the project.
    :param filename: String with the name of the file.
    :return: Full path to the file.
    """
    return os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'resources', filename)


def dict_equals(d1, d2):
    """
    Utility function that checks if two dictionaries are equals.
    :param d1: First dictionary to compare.
    :param d2: Second dictionary to compare.
    :return: Boolean that indicates if they are equals or not.
    """
    if len(d1.keys()) != len(d2.keys()) or len(d1.values()) != len(d2.values()):
        return False
    for key in d1.keys():
        if key not in d2.keys():
            return False
        if (isinstance(d1[key], str) and not isinstance(d2[key], str)) or (
                isinstance(d1[key], list) and not isinstance(d2[key], list)):
            return False
        if isinstance(d1[key], str) and d1[key] != d2[key]:
            return False
        if isinstance(d1[key], list) and set(d1[key]) != set(d2[key]):
            return False
    return True


class ScannerTest(unittest.TestCase):

    def _test_output(self, filename, expected_results):
        scanner = engine.file_managers.Scanner(path_composer(filename))
        file_analyzed = [token for token in scanner.scan()]
        for idx, val in enumerate(expected_results):
            self.assertEqual(val, file_analyzed[idx], "The output does not match the expectations.")

    def test_scan_file(self):
        """
        Tests a file with all the tokens existing in the template.
        """
        line1 = [(Tokens.VERBATIM, "verbatim"), (Tokens.BLANK, " "),
                 (Tokens.INIT_EXPRESSION, None), (Tokens.END_EXPRESSION, None), (Tokens.BLANK, " "),
                 (Tokens.INIT_EXPRESSION, None), (Tokens.BLANK, " "), (Tokens.END_EXPRESSION, None),
                 (Tokens.BLANK, " "),
                 (Tokens.INIT_LOOP, None), (Tokens.BLANK, " "), (Tokens.END_LOOP, None),
                 (Tokens.EOL, "\n")]
        self._test_output("scanner_elements.txt", line1)


class ParserTest(unittest.TestCase):

    def _test_parse(self, filename, expected_results):
        parser = engine.file_managers.Parser(engine.file_managers.Scanner(path_composer(filename)))
        file_analyzed = [construction for construction in parser.parse()]

        for idx, val in enumerate(expected_results):
            self.assertTrue(isinstance(type(val), type(file_analyzed[idx]) or
                                       issubclass(type(val), type(file_analyzed[idx]))))
            if type(val) == ReplacementElement.__class__:
                self.assertEqual(val.variable_name, file_analyzed[idx].variable_name, "Different vars")
            if type(val) == VerbatimElement.__class__:
                self.assertEqual(val.value, file_analyzed[idx].value, "Different vars")

    def test_parse_simple_replacement(self):
        expected_results = [VerbatimElement("hi"), BlankElement(), ReplacementElement("variable1"), EolElement(),
                            VerbatimElement("bye"), EolElement()]
        self._test_parse("parser_var.txt", expected_results)

    def test_parse_loop(self):
        expected_results = [LoopElement("array1", "item",
                                        [VerbatimElement("repeat"), BlankElement(),
                                         ReplacementElement("item"), BlankElement(),
                                         VerbatimElement("again"), EolElement()
                                         ]
                                        )
                            ]
        self._test_parse("parse_loop.txt", expected_results)

    # def test_parse_file(self):
    #     parser = engine.file_managers.Parser(engine.file_managers.Scanner(path_composer("parser_loop.txt")))
    #
    #     for c in parser.parse():
    #         print(c)


if __name__ == '__main__':
    unittest.main()
