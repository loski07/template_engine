import unittest

import lexical_analysis
import semantic_analysis
import symbol_table
import syntactical_analysis
from lexical_analisys_tests import path_composer


expected = """some random text
I wanted to say hello to you
some other text

do something with the a
do something with the b
do something with the c

now I say bye to everyone
more text

I might say hello to some and bye to others
is that okay?
"""


class SemanticAnalyzerTest(unittest.TestCase):
    """
    Unittest of the Semantics analyzer.
    """

    def _test_results(self, template_file_name, variable_file_name, expected_string):
        """
        Generic method that performs the test based on the init file and the expected results.
        :param template_file_name: String containing the name of the input file used as a template for the test.
        :param variable_file_name: String containing the name of the input file with the variables for the test.
        :param expected_string: String with the text to check against.
        """
        scanner = lexical_analysis.Scanner(path_composer(template_file_name))
        parser = syntactical_analysis.Parser(scanner)
        var_mgr = symbol_table.VariableManager(path_composer(variable_file_name))
        var_mgr.parse()
        translator = semantic_analysis.SemanticAnalyzer(parser, var_mgr)

        document = ""
        for chunk in translator.run():
            document += chunk

        self.assertEqual(expected_string, document)

    def test_analysis_plain_text(self):
        """
        Tests a translation for a file without any transformation.
        """
        self._test_results("template_no_replacements.txt", "correct_var_file.txt", expected)

    def test_analysis_string_replacements(self):
        """
        Tests a translation for a file with only string replacements.
        """
        self._test_results("template_string_replacements.txt", "correct_var_file.txt", expected)

    def test_analysis_simple_list_replacements(self):
        """
        Tests a translation for a file with string and simple list replacements.
        :return:
        """
        self._test_results("template_simple_list_replacements.txt", "correct_var_file.txt", expected)


if __name__ == '__main__':
    unittest.main()
