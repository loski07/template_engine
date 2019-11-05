import re
from abc import ABC
from engine import LexTokens, SyntaxElement


class SyntaxException(Exception):
    """
    Exception in the syntax of the template.
    """
    pass


class ParserElement(ABC):
    """
    Base class to store all the elements detected by the parser.
    """

    def __init__(self, element_type):
        """
        Constructor that initializes the object type.
        :param element_type: Constructions enumerate with the type.
        """
        self.type = element_type


class VerbatimElement(ParserElement):
    """
    Utility class to store a verbatim object
    """

    def __init__(self, value=None):
        """
        Constructor that initializes the object arguments.
        :param value: Value to store in the object.
        """
        super().__init__(SyntaxElement.VERBATIM)
        self.value = value


class BlankElement(VerbatimElement):
    """
    Special type of VerbatimElement that stores a blank space.
    """

    def __init__(self):
        """
        Constructor that initializes the object arguments.
        """
        super().__init__(SyntaxElement.VERBATIM)
        self.value = " "


class EolElement(VerbatimElement):
    """
    Special type of VerbatimElement that stores an end of line.
    """

    def __init__(self):
        """
        Constructor that initializes the object arguments.
        """
        super().__init__(SyntaxElement.VERBATIM)
        self.value = "\n"


class ReplacementElement(ParserElement):
    """
    Utility class to store a variable replacement element.
    """

    def __init__(self, variable_name=None):
        """
        Constructor that initializes the object arguments.
        :param variable_name: String with the name of the variable to replace.
        """
        super().__init__(SyntaxElement.REPLACEMENT)
        self.variable_name = variable_name


class LoopElement(ParserElement):
    """
    Utility class to store a loop element.
    """

    def __init__(self, variable_name=None, iterator_variable=None, loop_elements=None):
        """
        Constructor that initializes the object arguments.
        :param variable_name: String with the name of the variable to replace.
        :param iterator_variable: String with the name of the variable used as iterator.
        :param loop_elements: List of ParserElements that would be repeated.
        """
        super().__init__(SyntaxElement.LOOP)
        self.variable_name = variable_name
        self.iterator_variable = iterator_variable
        if loop_elements is None:
            self.loop_elements = []
        else:
            self.loop_elements = loop_elements


class Parser:
    """
    Syntactical parser for templates.
    """

    def __init__(self, scanner):
        """
        Constructor that initializes the attributes.
        :param scanner: engine.lexical_analysis.Scanner that performs the lexical analysis of the template file.
        """
        self._scanner = scanner

    def parse(self):
        """
        Parsing function that yields the different syntactical constructions found.
        :return: ParserElement with the next syntactical construction found.
        :raise: SyntaxException if it finds syntax errors in the template.
        """
        state = 0
        replacement_var = ""
        loop_contents = []
        loop_level = 0
        buffered_tokens = None
        scanner_generator = self._scanner.scan()
        while True:
            if buffered_tokens:
                item = buffered_tokens
                buffered_tokens = None
            else:
                item = next(scanner_generator, None)
                if not item:
                    break
            if state == 0:
                if item[0] in [LexTokens.EOL, LexTokens.BLANK, LexTokens.VERBATIM]:
                    verbatim_elem = VerbatimElement(item[1])
                    if loop_level == 0:
                        yield verbatim_elem
                        continue
                    else:
                        current_loop_object = loop_contents[loop_level - 1]
                        current_loop_object.loop_elements.append(verbatim_elem)
                        continue
                if item[0] == LexTokens.INIT_EXPRESSION:
                    state = 100
                    continue
                else:
                    raise SyntaxException("Invalid token {}".format(item([1])))

            if state == 100:  # "{{" found
                if item[0] == LexTokens.BLANK:
                    continue
                if item[0] == LexTokens.VERBATIM:
                    if not re.match(r"(?P<var>[a-zA-Z]\w*)", item[1]):
                        raise SyntaxException("Invalid replacement var name: {}".format(item[1]))
                    replacement_var = item[1]
                    state = 101
                    continue
                if item[0] == LexTokens.INIT_LOOP:
                    state = 200
                    continue
                if item[0] == LexTokens.END_LOOP:
                    state = 300
                    continue
                else:
                    raise SyntaxException("Invalid token {} after {{".format(item[1]))

            if state == 101:  # "{{ varName" found
                if item[0] == LexTokens.BLANK:
                    continue
                if item[0] == LexTokens.END_EXPRESSION:
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
                if item[0] == LexTokens.BLANK:
                    continue
                if item[0] == LexTokens.VERBATIM:
                    if not re.match(r"(?P<var>[a-zA-Z]\w*)", item[1]):
                        raise SyntaxException("Invalid replacement var name: {}".format(item[1]))
                    state = 201
                    loop_contents.insert(loop_level, LoopElement(item[1]))
                    continue
                else:
                    raise SyntaxException("Invalid token in the loop declaration {}".format(item[1]))

            if state == 201:  # "{{ #loop varName" found
                if item[0] == LexTokens.BLANK:
                    continue
                if item[0] == LexTokens.VERBATIM:
                    if not re.match(r"(?P<var>[a-zA-Z]\w*)", item[1]):
                        raise SyntaxException("Invalid replacement var name: {}".format(item[1]))
                    current_loop_object = loop_contents[loop_level - 1]
                    current_loop_object.iterator_variable = item[1]
                    state = 202
                    continue
                else:
                    raise SyntaxException("Invalid token in the loop declaration {}".format(item[1]))

            if state == 202:  # "{{ #loop varName iterator" found
                if item[0] == LexTokens.BLANK:
                    continue
                if item[0] == LexTokens.END_EXPRESSION:
                    state = 400
                    loop_level += 1
                    continue
                else:
                    raise SyntaxException("Invalid token in the loop declaration {}".format(item[1]))

            if state == 300:  # "{{ /loop" found
                if item[0] == LexTokens.BLANK:
                    continue
                if item[0] == LexTokens.END_EXPRESSION:
                    state = 400
                    loop_level -= 1
                    if loop_level == 0:
                        yield loop_contents[loop_level]
                    continue

            if state == 400:  # "{{ #loop varName iterator }} or {{ /loop }} found"
                state = 0
                if item[0] != LexTokens.EOL:
                    buffered_tokens = item
                continue
