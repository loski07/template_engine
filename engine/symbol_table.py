import ast
import re

import engine


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


class VariableManager(engine.BaseManager):
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
