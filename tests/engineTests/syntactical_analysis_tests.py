import os
import unittest

import engine.lexical_analysis
import engine.syntactical_analysis
from engine.syntactical_analysis import EolElement, BlankElement, VerbatimElement, ReplacementElement, LoopElement


def path_composer(filename):
    """
    Utility function that composes the path of a file in the test resources folder of the project.
    :param filename: String with the name of the file.
    :return: Full path to the file.
    """
    return os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'resources', filename)


class ParserTest(unittest.TestCase):
    """
    Unittests of the parser.
    """

    @staticmethod
    def _replacements_equal(expected, obtained):
        """
        Compares if the engine.syntactical_analysis.ReplacementElement are the same.
        :param expected: engine.syntactical_analysis.ReplacementElement expected.
        :param obtained: engine.syntactical_analysis.ReplacementElement obtained.
        :return: Boolean saying whether the objects are equals of not.
        """
        same_type = isinstance(type(expected), type(obtained)) or issubclass(type(expected), type(obtained))
        same_value = expected.variable_name == obtained.variable_name
        return same_type and same_value

    @staticmethod
    def _verbatim_equal(expected, obtained):
        """
        Compares if the engine.syntactical_analysis.VerbatimElement are the same.
        :param expected: engine.syntactical_analysis.VerbatimElement expected.
        :param obtained: engine.syntactical_analysis.VerbatimElement obtained.
        :return: Boolean saying whether the objects are equals of not.
        """
        same_type = isinstance(type(expected), type(obtained)) or issubclass(type(expected), type(obtained))
        same_value = expected.value == obtained.value
        return same_type and same_value

    @staticmethod
    def _loop_equal(expected, obtained):
        """
        Compares if the engine.syntactical_analysis.LoopElement are the same.
        :param expected: engine.syntactical_analysis.LoopElement expected.
        :param obtained: engine.syntactical_analysis.LoopElement obtained.
        :return: Boolean saying whether the objects are equals of not.
        """
        same_type = isinstance(type(expected), type(obtained)) or issubclass(type(expected), type(obtained))
        same_value = expected.variable_name == obtained.variable_name
        same_value = same_value and expected.iterator_variable == obtained.iterator_variable
        for idx, obtained_loop_item in enumerate(obtained.loop_elements):
            expected_loop_item = expected.loop_elements[idx]
            if type(obtained_loop_item) == ReplacementElement:
                same_value = same_value and ParserTest._replacements_equal(
                    expected_loop_item, obtained_loop_item)
            elif type(obtained_loop_item) in [VerbatimElement, BlankElement, EolElement]:
                same_value = same_value and ParserTest._verbatim_equal(expected_loop_item, obtained_loop_item)
            else:
                same_value = same_value and ParserTest._loop_equal(expected_loop_item, obtained_loop_item)
            if not same_value:
                return False
        return same_type and same_value

    def _test_parse(self, filename, expected_results):
        """
        Generic method that performs the test based on the init file and the expected results.
        :param filename: String containing the name of the input file used for the test.
        :param expected_results: List of engine.file_managers.ParserElements to check against.
        """
        parser = engine.syntactical_analysis.Parser(engine.lexical_analysis.Scanner(path_composer(filename)))
        file_analyzed = [construction for construction in parser.parse()]

        for idx, expected in enumerate(expected_results):
            obtained = file_analyzed[idx]
            if type(expected) == ReplacementElement:
                self.assertTrue(ParserTest._replacements_equal(expected, obtained))
            elif type(expected) in [VerbatimElement, BlankElement, EolElement]:
                self.assertTrue(ParserTest._verbatim_equal(expected, obtained))
            else:
                self.assertTrue(ParserTest._loop_equal(expected, obtained))

    def test_parse_simple_replacement(self):
        """
        Tests the parsing of a file with simple string replacements.
        """
        expected_results = [VerbatimElement("hi"), BlankElement(), ReplacementElement("variable1"), EolElement(),
                            VerbatimElement("bye"), EolElement()]
        self._test_parse("parser_var.txt", expected_results)

    def test_parse_simple_replacement_wrong(self):
        """
        Tests the parsing of a file with simple string replacement but wrong syntax.
        """
        with self.assertRaises(engine.syntactical_analysis.SyntaxException):
            engine.syntactical_analysis.SyntaxException, self._test_parse("parser_var_wrong_extra.txt", [])

    def test_parse_loop(self):
        """
        Tests the parsing of a file with simple loops.
        """
        expected_results = [LoopElement("array1", "item",
                                        [VerbatimElement("repeat"), BlankElement(),
                                         ReplacementElement("item"), BlankElement(),
                                         VerbatimElement("again"), EolElement()
                                         ]
                                        )
                            ]
        self._test_parse("parser_loop.txt", expected_results)

    def test_parse_loop_with_extra_var(self):
        """
        Tests the parsing of a file with simple string replacements together with a simple loop.
        """
        expected_results = [LoopElement("array1", "item",
                                        [VerbatimElement("repeat"), BlankElement(),
                                         ReplacementElement("item"), BlankElement(),
                                         VerbatimElement("again"), BlankElement(),
                                         ReplacementElement("var1"), EolElement()
                                         ]
                                        )
                            ]
        self._test_parse("parser_loop_with_extra_var.txt", expected_results)

    def test_parse_loop_with_extra_loop(self):
        """
        Tests the parsing of a file with a loop embedded in another loop.
        """
        expected_results = [LoopElement("array1", "item",
                                        [VerbatimElement("repeat"), BlankElement(),
                                         ReplacementElement("item"), BlankElement(),
                                         VerbatimElement("again"), BlankElement(),
                                         ReplacementElement("var1"), EolElement(),
                                         LoopElement("array2", "item2", [
                                             VerbatimElement("crossing"), BlankElement(),
                                             VerbatimElement("fingers"), BlankElement(),
                                             ReplacementElement("item2"), EolElement()])
                                         ])
                            ]
        self._test_parse("parser_loop_with_extra_var.txt", expected_results)

    def test_parse_loop_wrong_init_token(self):
        """
        Tests the parsing of a file with a loop with a wrong init token syntax.
        """
        with self.assertRaises(engine.syntactical_analysis.SyntaxException):
            self._test_parse("parser_loop_wrong_init_token.txt", [])

    def test_parse_loop_wrong_end_token(self):
        """
        Tests the parsing of a file with a loop with a wrong end token syntax.
        """
        with self.assertRaises(engine.syntactical_analysis.SyntaxException):
            self._test_parse("parser_loop_wrong_end_token.txt", [])

    def test_parse_loop_wrong_less_params(self):
        """
        Tests the parsing of a file with a loop with a wrong syntax because it has less tokens in the loop.
        """
        with self.assertRaises(engine.syntactical_analysis.SyntaxException):
            self._test_parse("parser_loop_wrong_less_params.txt", [])

    def test_parse_loop_wrong_more_params(self):
        """
        Tests the parsing of a file with a loop with a wrong syntax because it has more tokens in the loop.
        """
        with self.assertRaises(engine.syntactical_analysis.SyntaxException):
            self._test_parse("parser_loop_wrong_more_params.txt", [])

if __name__ == '__main__':
    unittest.main()
