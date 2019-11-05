#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import argparse
import logging
import os

import lexical_analysis
import semantic_analysis
import symbol_table
import syntactical_analysis
try:
    from argcomplete import autocomplete
except ImportError:
    # If module argcomplete is not available, just skip the completion
    def autocomplete(_):
        pass


class OutputFileManager:
    """
    Class that manages the output file.
    """

    def __init__(self, filepath):
        """
        Constructor that initializes the arguments of the object.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.filepath = filepath

    def __enter__(self):
        """
        Context manager that allows declaring the object in a with statement.
        :return:
        """
        if os.path.isfile(self.filepath):
            self.logger.warning("The file {} already exists. It will be truncated".format(self.filepath))
        self.file = open(self.filepath, 'w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager to close the file at the end of the with statement.
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        """
        if not self.file.closed:
            self.file.close()

    def print(self, chunk):
        """
        Prints the specified chunk of text in the output file.
        :param chunk: String with the text to print.
        """
        self.file.write(chunk)


class Template:
    """
    Class that performs the complete replacement of the placeholders of the template.
    """

    def __init__(self, template_path, variables_path, output_path):
        """
        Constructor that initializes the object arguments.
        :param template_path: String containing the path to the template file to analyze.
        :param variables_path: String containing the path to the variables file.
        """
        scanner = lexical_analysis.Scanner(template_path)
        self.parser = syntactical_analysis.Parser(scanner)
        self.var_mgr = symbol_table.VariableManager(variables_path)
        self.translator = semantic_analysis.SemanticAnalyzer(self.parser, self.var_mgr)
        self.out_path = output_path

    def replace(self):
        """
        Performs the replacement of the placeholders in the file to the corresponding value in the variable file
        writing the output in the output file.
        """
        self.var_mgr.parse()
        with OutputFileManager(self.out_path) as out_mgr:
            for chunk in self.translator.run():
                out_mgr.print(chunk)


def parse_command_line():
    """
    Parses the user input.
    :return: argparse.Namespace with the user input.
    """
    parser = argparse.ArgumentParser(
        description="Template processor that replaces placeholders in the template file for the variables in the"
                    " variable file writing the output to the the output file.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-t", "--template_file_path", required=True, default=None, action="store",
                        help="Path to the template file.")
    parser.add_argument("-v", "--variables_file_path", required=True, default=None, action="store",
                        help="Path to the variables file.")
    parser.add_argument("-o", "--output_file_path", required=True, default=None, action="store",
                        help="Path to the output file.")

    autocomplete(parser)
    return parser.parse_args()


def main():
    """
    Main function of the module. Executes the translation.
    """
    args = parse_command_line()
    template = Template(args.template_file_path, args.variables_file_path, args.output_file_path)
    template.replace()


if __name__ == '__main__':
    main()
