from syntactical_analysis import LoopElement, VerbatimElement, ReplacementElement


class SemanticAnalyzer:
    """
    Class that performs the translation of the template placeholders into their final result.
    """

    def __init__(self, parser, variable_manager):
        """
        Constructor that initializes the object arguments.
        :param parser: engine.syntactical_analysis.Parser object that provides the syntax elements.
        :param variable_manager: engine.symbol_table.VariableManager that contains the replacement variables.
        """
        self.parser = parser
        self.var_mgr = variable_manager

    def _translate(self, parser_element):
        """
        Translates the syntactical element received.
        :param parser_element: engine.syntactical_analysis.ParserElement to translate.
        :return: String with the translation.
        :raise: FileParseException if the file has not yet been parsed.
        :raise: VariableNotFound if the variable was not in the file.
        :raise: VariableHiddenException if a variable with the same name already exists.
        """
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
        """
        Performs the translation of the whole template returning the translated elements one by one.
        :return: String containing the next translated element.
        :raise: FileParseException if the file has not yet been parsed.
        :raise: VariableNotFound if the variable was not in the file.
        :raise: VariableHiddenException if a variable with the same name already exists.
        """
        for item in self.parser.parse():
            for translation in self._translate(item):
                yield translation
