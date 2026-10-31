# -*- coding: utf-8 -*-

import argparse
import os
import tempfile
import unittest

from mhsg import __main__ as mhsg_main, config


class test_index_files(unittest.TestCase):
    def setUp(self):
        self.oDirectory = tempfile.TemporaryDirectory()
        self.sDirectory = self.oDirectory.name
        os.makedirs(os.path.join(self.sDirectory, "tb"))
        for sName in ["design.vhd", os.path.join("tb", "tb_a.vhd"), os.path.join("tb", "tb_b.vhd")]:
            with open(os.path.join(self.sDirectory, sName), "w", encoding="utf-8") as oFile:
                oFile.write("")

    def tearDown(self):
        self.oDirectory.cleanup()

    def test_index_file_list_is_globbed(self):
        sPattern = os.path.join(self.sDirectory, "tb", "*.vhd")
        dConfiguration = config.process_config_file({}, {"index_file_list": [sPattern]}, "config.yaml")
        self.assertEqual(
            sorted(os.path.join(self.sDirectory, "tb", sName).replace("\\", "/") for sName in ["tb_a.vhd", "tb_b.vhd"]),
            sorted(dConfiguration["index_file_list"]),
        )

    def test_index_file_list_does_not_add_files_to_analyze(self):
        sDesign = os.path.join(self.sDirectory, "design.vhd")
        sTestbench = os.path.join(self.sDirectory, "tb", "tb_a.vhd")
        oArguments = argparse.Namespace(filename=[sDesign], index_files=[])
        config.update_command_line_arguments(oArguments, {"index_file_list": [sTestbench]})
        self.assertEqual([sDesign], oArguments.filename)
        self.assertEqual([sTestbench], oArguments.index_files)

    def test_get_index_files(self):
        sDesign = os.path.join(self.sDirectory, "design.vhd")
        sPattern = os.path.join(self.sDirectory, "tb", "*.vhd")
        oArguments = argparse.Namespace(filename=[sDesign], index_files=[sPattern, sDesign])
        lFiles = mhsg_main.get_index_files(oArguments)
        self.assertEqual(sDesign, lFiles[0])
        self.assertEqual(3, len(lFiles))
        self.assertEqual(
            sorted(os.path.join(self.sDirectory, "tb", sName) for sName in ["tb_a.vhd", "tb_b.vhd"]),
            sorted(lFiles[1:]),
        )
