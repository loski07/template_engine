import unittest
import os
import engine.file_managers


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


if __name__ == '__main__':
    unittest.main()
