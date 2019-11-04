#!/usr/bin/env python
import os
import logging
from engine.syntactical_analysis import LoopElement, VerbatimElement, ReplacementElement


class SemanticsAnalyzer:

    def __init__(self, parser, variable_manager):
        self.parser = parser
        self.var_mgr = variable_manager

    def _translate(self, parser_element):
        if isinstance(parser_element, VerbatimElement) or issubclass(parser_element.__class__, VerbatimElement):
            yield parser_element.value
        if isinstance(parser_element, ReplacementElement) or issubclass(parser_element.__class__, ReplacementElement):
            yield self.var_mgr.get_replacement(parser_element.variable_name)
        if isinstance(parser_element, LoopElement) or issubclass(parser_element.__class__, LoopElement):
            translated_elements = []
            loop_array = self.var_mgr.get_replacement(parser_element.variable_name)
            for var_value in loop_array:
                self.var_mgr.add_loop_variable(parser_element.iterator_variable, var_value)
                for expr in parser_element.loop_elements:
                    gen = self._translate(expr)
                    for el in gen:
                        translated_elements.append(el)
                self.var_mgr.delete_loop_variable(parser_element.iterator_variable)
            yield "".join(translated_elements)

    def run(self):
        buffer = ""
        for item in self.parser.parse():
            for translation in self._translate(item):
                yield translation


class OutputFileManager:
    """
    Class that manages the output file.
    """

    def __init__(self, filepath):
        """
        Constructor that initializes the arguments of the object.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        if os.path.isfile(filepath):
            self.logger.warning("The file {} already exists. It will be truncated".format(filepath))
        self.file = open(filepath, 'w')

    def __del__(self):
        """
        Destructor tha closes the output file.
        """
        self.file.close()

    def print(self, lines):
        """
        Prints the specified lines in the output file.
        :param lines: List of strings with the lines to print.
        """
        self.file.writelines(lines)
