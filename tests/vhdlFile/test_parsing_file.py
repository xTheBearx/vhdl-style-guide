# -*- coding: utf-8 -*-
import os
import unittest

from mhsg import vhdlFile
from tests import utils

try:
    sLrmUnit = os.environ["mhsg_file_to_parse"]

    lFile, eError = vhdlFile.utils.read_vhdlfile(sLrmUnit)
    oFile = vhdlFile.vhdlFile(lFile)

    class test_token(unittest.TestCase):
        def test_debug(self):
            utils.print_objects(oFile, True)

except KeyError:
    pass
