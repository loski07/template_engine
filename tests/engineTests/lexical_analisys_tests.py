import os
import unittest

import engine.lexical_analysis
from utils import LexTokens


def path_composer(filename):
    """
    Utility function that composes the path of a file in the test resources folder of the project.
    :param filename: String with the name of the file.
    :return: Full path to the file.
    """
    return os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'resources', filename)


class ScannerTest(unittest.TestCase):
    """
    Unittests of the scanner.
    """

    def _test_output(self, filename, expected_results):
        """
        Generic method that performs the test based on the init file and the expected results.
        :param filename: String containing the name of the input file used for the test.
        :param expected_results: List of tuples containing the engine.file_managers.Token enumerate and a string or None
        """
        scanner = engine.lexical_analysis.Scanner(path_composer(filename))
        file_analyzed = [token for token in scanner.scan()]
        for idx, expected in enumerate(expected_results):
            obtained = file_analyzed[idx]
            self.assertTrue(expected[0] == obtained[0], "The type of token is not the same.")
            self.assertEqual(expected[1], obtained[1], "The contents of the token are not the same.")

    def test_scan_file(self):
        """
        Tests a file with all the tokens existing in the template.
        """
        line1 = [(LexTokens.VERBATIM, "verbatim"), (LexTokens.BLANK, " "),
                 (LexTokens.INIT_EXPRESSION, None), (LexTokens.END_EXPRESSION, None), (LexTokens.BLANK, " "),
                 (LexTokens.INIT_EXPRESSION, None), (LexTokens.BLANK, " "), (LexTokens.END_EXPRESSION, None),
                 (LexTokens.BLANK, " "),
                 (LexTokens.INIT_LOOP, None), (LexTokens.BLANK, " "), (LexTokens.END_LOOP, None),
                 (LexTokens.EOL, "\n")]
        self._test_output("scanner_elements.txt", line1)


if __name__ == '__main__':
    unittest.main()
