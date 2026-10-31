# -*- coding: utf-8 -*-


class New:
    def __init__(self, sName):
        self.name = sName
        self.value = None
        self.analyze_function = None
        self.analysis_options = None

    def analyze(self, oToi):
        return self.analyze_function(self, oToi)  # pylint: disable=not-callable  # set by the rule which creates the option
