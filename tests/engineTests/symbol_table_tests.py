import unittest
from engine.symbol_table import VariableManager, FileParseException, LineParseException
from lexical_analisys_tests import path_composer


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
            token, value = VariableManager._parse_line('"token": "value"')
            self.assertEqual(token, 'token', 'It did not obtain the token expected')
            self.assertEqual(value, 'value', 'It did not obtain the value expected')
        except FileParseException:
            self.fail('Exception parsing the entry')

    def test_parse_correct_line_list(self):
        """
        Test of the parsing method with correct entry when the value is a list.
        """
        try:
            token, value = VariableManager._parse_line('"token": ["value1", "value2", "value3"]')
            self.assertEqual(token, 'token', 'It did not obtain the token expected')
            self.assertIsInstance(value, list, 'The value is not a list')
            self.assertListEqual(
                value, ["value1", "value2", "value3"], 'The list obtained is not equal to the original')
        except FileParseException:
            self.fail('Exception parsing the entry')

    def test_parse_incorrect_line_token_wrong(self):
        """
        Test of the parsing method with wrong entry when the token is wrong.
        """
        try:
            VariableManager._parse_line('"tok":en": "value"')
            self.fail('It should have failed but somehow it went through')
        except FileParseException:
            pass

    def test_parse_incorrect_line_string_value_wrong(self):
        """
        Test of the parsing method with a wrong entry when the value is a malformed string.
        """
        try:
            for l in ['"token": "val"ue"', '"token": val"ue"', '"token": val"ue']:
                VariableManager._parse_line(l)
                self.fail('It should have failed but somehow it went through with {}'.format(l))
        except FileParseException:
            pass

    def test_parse_incorrect_line_list_value_wrong(self):
        """
        Test of the parsing method with a wrong entry when the value is a list of malformed strings or a malformed
        list of correct strings or a malformed list of malformed strings.
        """
        try:
            for l in ['"token": ["val"ue"]', '"token": [val"ue"]', '"token": [val"ue]', '"token": val"ue]',
                      '"token": [val"ue']:
                VariableManager._parse_line(l)
                self.fail('It should have failed but somehow it went through with {}'.format(l))
        except FileParseException:
            pass

    def _test_parse_correct_file(self, filename):
        """
        Utility method to test the results of reading a correct var file.
        :param filename: String with the name of the file to read.
        """
        try:
            mgr = VariableManager(path_composer(filename))
            mgr.parse()
            self.assertTrue(VariableManagerTests.target_dict, mgr._variables)
        except IOError:
            self.fail('I could not find the file {}'.format(filename))
        except LineParseException as e:
            self.fail(e)

    def test_parse_correct_file(self):
        """
        Tests a nice input file.
        """
        self._test_parse_correct_file('correct_var_file.txt')

    def test_parse_correct_file_duplicates(self):
        """
        Tests a correct input file but with duplicated variables.
        """
        self._test_parse_correct_file('correct_var_file_duplicates.txt')

    def test_parse_correct_file_scrambled(self):
        """
        Tests a correct input file with more spaces around.
        """
        self._test_parse_correct_file('correct_var_file_scrambled.txt')


if __name__ == '__main__':
    unittest.main()
