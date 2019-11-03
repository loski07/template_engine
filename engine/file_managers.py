#!/usr/bin/env python
import os
import re
import ast
import logging
import queue
import enum
from abc import ABC, abstractmethod


class FileParseException(Exception):
    """
    Base class for the exception raised when parsing the input files
    """
    pass


class LineParseException(FileParseException):
    """
    Exception for errors in line parse of input files.
    """
    pass


class TokenParseException(LineParseException):
    """
    Exception in variable token parsing.
    """
    pass


class ValueParseException(LineParseException):
    """
    Exception in variable value parsing.
    """
    pass


class VariableNotFound(KeyError):
    """
    Exception finding a replacement variable.
    """
    pass

class SyntaxException(Exception):
    """
    Exception in the syntax of the template.
    """
    pass

class _BaseManager(ABC):
    """
    Abstract class that defines the generic methods for all the Managers.
    """

    @abstractmethod
    def __init__(self, filepath):
        """
        Constructor that initializes the arguments of the object.
        :param filepath: String containing the path of the input file.
        :raise IOError when there is no file with such path.
        """
        self._filepath = filepath
        self.logger = logging.getLogger(self.__class__.__name__)
        if not os.path.isfile(filepath):
            raise IOError("File {} not found".format(self._filepath))


class VariableManager(_BaseManager):
    """
    Class that manages the replacement variables of the template engine.
    """

    def __init__(self, filepath):
        """
        Constructor that initializes the arguments of the object.
        :param filepath: String containing the path of the replacements file.
        :raise IOError when there is no file with such path.
        """
        super().__init__(filepath)
        self._variables = None

    @staticmethod
    def _parse_line(line):
        """
        Parses the input line to obtain the variable to be replaced and the value.
        Further explanation of the regular expression in https://regex101.com/r/Grx1GN/2
        :param line: Input line to parse.
        :return: String with the name of the variable and a string or a list of strings with the replacement value.
        :raise LineParseException if the line has syntax errors.
        :raise TokenParseException if no token could be found in the line.
        :raise ValueParseException if no value could be found in the line.
        """
        matching_regex = r' *"(?P<token>[a-zA-Z]\w*)" *: *(?P<value>(("[^"]*")|\["[^"]*"(( *, *"[^"]*")+)\])) *$'
        result = re.search(matching_regex, line)
        if not result:
            raise LineParseException("The line '{}' does not have the correct syntax.".format(line))
        if not result.group('token'):
            raise TokenParseException("Unable to find a token to replace in '{}'".format(line))
        if not result.group('value'):
            raise ValueParseException("Unable to find a replacement value in '{}'".format(line))
        return result.group('token'), ast.literal_eval(result.group('value'))

    def parse(self):
        """
        Parses the whole replacements file updating the dictionary `self._variables` with the elements found.
        """
        self._variables = {}
        with open(self._filepath, 'r') as f:
            for line in f:
                line = line.strip(' \r\n')
                if len(line) > 0:
                    token, value = VariableManager._parse_line(line)
                    if token in self._variables:
                        self.logger.warning("The variable '{}' has already been defined".format(token))
                    self._variables[token] = value
            if len(self._variables.keys()) == 0:
                self.logger.warning("No variables found in the replacements file")

    def get_replacement(self, key):
        """
        Gets the replacement value for the requested variable.
        :param key: String containing the variable name.
        :return: String or List with the replacement value.
        :raise FileParseException if the file has not yet been parsed.
        :raise VariableNotFound if the variable was not in the file.
        """
        if not self._variables:
            raise FileParseException("The file {} has not been parsed yet".format(self._filepath))
        if key in self._variables:
            return self._variables[key]
        else:
            raise VariableNotFound("The variable '{}' was not defined in the file '{}'".format(key, self._filepath))


class Tokens(enum.Enum):
    VERBATIM = 1
    INIT_EXPRESSION = 2
    END_EXPRESSION = 3
    INIT_LOOP = 4
    END_LOOP = 5
    BLANK = 6
    EOL = 7


class Scanner(_BaseManager):
    """
    Class that performs a lexical analysis of the template.
    """

    def __init__(self, filepath):
        """
        Constructor that initializes the arguments of the object.
        :param filepath: String containing the path of the template file.
        :raise IOError when there is no file with such path.
        """
        super().__init__(filepath)
    #     self.file = open(filepath, 'r')
    #
    # def __del__(self):
    #     """
    #     Destructor tha closes the output file.
    #     """
    #     self.file.close()

    def scan(self):
        with open(self._filepath, 'r') as template_file:
            for line in template_file:
                # Remove the \n character at the end of the line
                line = line[:-1]

                line = re.findall(r"{{2}|}{2}|[^ \n{}]*", line)
                # Removes the last empty token generated by the regex.
                line = line[:-1]

                for word in line:
                    if word == '{{':
                        yield Tokens.INIT_EXPRESSION, None
                    elif word == '}}':
                        yield Tokens.END_EXPRESSION, None
                    elif word == '#loop':
                        yield Tokens.INIT_LOOP, None
                    elif word == '/loop':
                        yield Tokens.END_LOOP, None
                    elif word == "":
                        yield Tokens.BLANK, " "
                    else:
                        yield Tokens.VERBATIM, word
                yield Tokens.EOL, "\n"


class Constructions(enum.Enum):
    VERBATIM = 0
    REPLACEMENT = 1
    LOOP = 2


class ParserElement(ABC):
    def __init__(self, element_type):
        self.type = element_type


class VerbatimElement(ParserElement):

    def __init__(self, value=None):
        super().__init__(Constructions.VERBATIM)
        self.value = value


class BlankElement(VerbatimElement):
    def __init__(self):
        super().__init__(Constructions.VERBATIM)
        self.value = " "


class EolElement(VerbatimElement):
    def __init__(self):
        super().__init__(Constructions.VERBATIM)
        self.value = "/n"


class ReplacementElement(ParserElement):

    def __init__(self, variable_name=None):
        super().__init__(Constructions.REPLACEMENT)
        self.variable_name = variable_name


class LoopElement(ParserElement):

    def __init__(self, variable_name=None, iterator_variable=None, loop_elements=None):
        super().__init__(Constructions.LOOP)
        self.variable_name = variable_name
        self.iterator_variable = iterator_variable
        if loop_elements is None:
            self.loop_elements = []
        else:
            self.loop_elements = loop_elements


class Parser:
    def __init__(self, scanner):
        self._scanner = scanner
        # self._var_manager = var_manager
        self._queue = queue.SimpleQueue()

    def parse(self):
        state = 0
        replacement_var = ""
        iterator_var = ""
        loop_contents = []
        loop_level = 0
        for item in self._scanner.scan():
            if state == 0:
                if item[0] in [Tokens.EOL, Tokens.BLANK, Tokens.VERBATIM]:
                    verbatim_elem = VerbatimElement(item[1])
                    if loop_level == 0:
                        yield verbatim_elem
                        continue
                    else:
                        current_loop_object = loop_contents[loop_level - 1]
                        current_loop_object.loop_elements.append(verbatim_elem)
                        continue
                if item[0] == Tokens.INIT_EXPRESSION:
                    state = 100
                    continue
                else:
                    raise SyntaxException("Invalid token {}".format(item([1])))

            if state == 100:  # "{{" found
                if item[0] == Tokens.BLANK:
                    continue
                if item[0] == Tokens.VERBATIM:
                    if not re.match(r"(?P<var>[a-zA-Z]\w*)", item[1]):
                        raise SyntaxException("Invalid replacement var name: {}".format(item[1]))
                    replacement_var = item[1]
                    state = 101
                    continue
                if item[0] == Tokens.INIT_LOOP:
                    state = 200
                    continue
                if item[0] == Tokens.END_LOOP:
                    state = 300
                    continue
                else:
                    raise SyntaxException("Invalid token {} after {{".format(item[1]))

            if state == 101:  # "{{ varName" found
                if item[0] == Tokens.BLANK:
                    continue
                if item[0] == Tokens.END_EXPRESSION:
                    replacement_elem = ReplacementElement(replacement_var)
                    state = 0
                    if loop_level == 0:
                        yield replacement_elem
                        continue
                    else:
                        current_loop_object = loop_contents[loop_level - 1]
                        current_loop_object.loop_elements.append(replacement_elem)
                        continue
                else:
                    raise SyntaxException("Invalid token in a variable replacement construction {}".format(item[1]))

            if state == 200:  # "{{ #loop" found
                if item[0] == Tokens.BLANK:
                    continue
                if item[0] == Tokens.VERBATIM:
                    if not re.match(r"(?P<var>[a-zA-Z]\w*)", item[1]):
                        raise SyntaxException("Invalid replacement var name: {}".format(item[1]))
                    state = 201
                    loop_contents.insert(loop_level, LoopElement(item[1]))
                    continue
                else:
                    raise SyntaxException("Invalid token in the loop declaration {}".format(item[1]))

            if state == 201:  # "{{ #loop varName" found
                if item[0] == Tokens.BLANK:
                    continue
                if item[0] == Tokens.VERBATIM:
                    if not re.match(r"(?P<var>[a-zA-Z]\w*)", item[1]):
                        raise SyntaxException("Invalid replacement var name: {}".format(item[1]))
                    current_loop_object = loop_contents[loop_level - 1]
                    current_loop_object.iterator_variable = item[1]
                    state = 202
                    continue
                else:
                    raise SyntaxException("Invalid token in the loop declaration {}".format(item[1]))

            if state == 202:  # "{{ #loop varName iterator" found
                if item[0] == Tokens.BLANK:
                    continue
                if item[0] == Tokens.END_EXPRESSION:
                    state = 0
                    loop_level += 1
                    continue
                else:
                    raise SyntaxException("Invalid token in the loop declaration {}".format(item[1]))

            if state == 300:  # "{{ /loop" found
                if item[0] == Tokens.BLANK:
                    continue
                if item[0] == Tokens.END_EXPRESSION:
                    state = 0
                    loop_level -= 1
                    if loop_level == 0:
                        yield loop_contents[loop_level]
                    continue


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
