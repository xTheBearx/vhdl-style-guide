# -*- coding: utf-8 -*-


class ClassifyError(Exception):
    """
    Exception raised for errors when classifying VHDL Files.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    def set_filename(self, sFilename):
        """
        Names the file in the message, which is built before the file name is known.
        """
        if sFilename is not None:
            self.message = self.message.replace(" in file None", " in file " + str(sFilename))


class ConfigurationError(Exception):
    """
    Exception raised for errors when configuration MHSG..
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class DesignError(Exception):
    """
    Exception raised when design analysis cannot run, for example because a tool is missing.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message
