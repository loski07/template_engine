#!/usr/bin/env python
import os
import logging


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
