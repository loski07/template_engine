import unittest

import engine.lexical_analysis
import engine.syntactical_analysis
from engine.syntactical_analysis import EolElement, BlankElement, VerbatimElement, ReplacementElement, LoopElement
from tests.engineTests import path_composer


class ParserTest(unittest.TestCase):
    """
    Unittests of the parser.
    """

    @staticmethod
    def _replacements_equal(expected, obtained):
        same_type = isinstance(type(expected), type(obtained)) or issubclass(type(expected), type(obtained))
        same_value = expected.variable_name == obtained.variable_name
        return same_type and same_value

    @staticmethod
    def _verbatim_equal(expected, obtained):
        same_type = isinstance(type(expected), type(obtained)) or issubclass(type(expected), type(obtained))
        same_value = expected.value == obtained.value
        return same_type and same_value

    @staticmethod
    def _loop_equal(expected, obtained):
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
        expected_results = [VerbatimElement("hi"), BlankElement(), ReplacementElement("variable1"), EolElement(),
                            VerbatimElement("bye"), EolElement()]
        self._test_parse("parser_var.txt", expected_results)

    def test_parse_loop(self):
        expected_results = [LoopElement("array1", "item",
                                        [EolElement(), VerbatimElement("repeat"), BlankElement(),
                                         ReplacementElement("item"), BlankElement(),
                                         VerbatimElement("again"), EolElement()
                                         ]
                                        )
                            ]
        self._test_parse("parser_loop.txt", expected_results)

    def test_parse_loop_with_extra_var(self):
        expected_results = [LoopElement("array1", "item",
                                        [EolElement(), VerbatimElement("repeat"), BlankElement(),
                                         ReplacementElement("item"), BlankElement(),
                                         VerbatimElement("again"), BlankElement(),
                                         ReplacementElement("var1"), EolElement()
                                         ]
                                        )
                            ]
        self._test_parse("parser_loop_with_extra_var.txt", expected_results)

    def test_parse_loop_with_extra_loop(self):
        expected_results = [LoopElement("array1", "item",
                                        [EolElement(), VerbatimElement("repeat"), BlankElement(),
                                         ReplacementElement("item"), BlankElement(),
                                         VerbatimElement("again"), BlankElement(),
                                         ReplacementElement("var1"), EolElement(),
                                         LoopElement("array2", "item2", [
                                             EolElement(), VerbatimElement("crossing"), BlankElement(),
                                             VerbatimElement("fingers"), BlankElement(),
                                             ReplacementElement("item2"), EolElement()])
                                         ])
                            ]
        self._test_parse("parser_loop_with_extra_var.txt", expected_results)


if __name__ == '__main__':
    unittest.main()
