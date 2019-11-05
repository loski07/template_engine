import os
import unittest
import tempfile
from translator import OutputFileManager, Template
from lexical_analisys_tests import path_composer


class OutputFileManagerTest(unittest.TestCase):
    """
    Test for the OutputFileManager class
    """
    def test_print(self):
        out_file = tempfile.NamedTemporaryFile()
        out_file_path = os.path.join(tempfile.gettempdir(), out_file.name)
        out_file.close()

        expected = [
            "Darkness is ignorance\n",
            "Knowledge is light\n",
            "Fight only with yourself\n",
            "Or the shadows of the night\n",
        ]

        with OutputFileManager(out_file_path) as out_mgr:
            out_mgr.print("Darkness is ignorance\n")
            out_mgr.print("Knowledge")
            out_mgr.print(" is ")
            out_mgr.print("light\nFight only with yourself\n")
            out_mgr.print("Or the shadows ")
            out_mgr.print("of the night\n")

        with open(out_file_path, 'r') as f:
            test_line_idx = 0
            for line in f:
                self.assertEqual(expected[test_line_idx], line)
                test_line_idx += 1


class TemplateTest(unittest.TestCase):

    def test_replace_correct(self):
        out_file = tempfile.NamedTemporaryFile()
        out_file_path = os.path.join(tempfile.gettempdir(), out_file.name)
        out_file.close()
        template = Template(
            path_composer("template_simple_list_replacements.txt"),
            path_composer("correct_var_file.txt"),
            out_file_path)
        template.replace()

        with open(out_file_path, 'r') as f_generated, open(path_composer("template_no_replacements.txt")) as f_expected:
            for line_generated in f_generated:
                line_expected = f_expected.readline()
                self.assertEqual(line_expected, line_generated)


if __name__ == '__main__':
    unittest.main()
