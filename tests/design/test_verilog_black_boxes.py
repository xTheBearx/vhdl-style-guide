# -*- coding: utf-8 -*-
"""The modules a Verilog design instantiates but no file defines, see mhsg/design/verilog_black_boxes.py."""

import fnmatch
import os
import shutil
import tempfile
import unittest

import yaml

from mhsg.design import black_box, tools, verilog_black_boxes


class Design:
    def __init__(self, dBlackBoxes):
        self.black_boxes = black_box.from_design({"black_boxes": dBlackBoxes})


class test_stubs(unittest.TestCase):
    def test_directions_from_roles(self):
        oDesign = Design(
            {
                "vendor_ip": {
                    "ports": {
                        "aclk": "clock",
                        "y_o": {"path": ["a_i"]},
                        "irq": "async",
                        "cfg": {"static": "Set at boot"},
                    },
                },
            },
        )
        dInstances = {"parameters": ["WIDTH"], "ordered_parameters": 0, "ports": ["aclk", "irq", "y_o", "spare"], "ordered_ports": 0}
        self.assertEqual(
            "(* mhsg_inferred_directions *) module vendor_ip #(parameter WIDTH = 0) "
            "(input wire aclk, inout wire irq, output wire y_o, inout wire spare, input wire a_i, input wire cfg);\nendmodule\n",
            verilog_black_boxes.stub(oDesign, "vendor_ip", dInstances),
        )

    def test_no_inout_no_attribute(self):
        oDesign = Design({"pll": {"ports": {"clk_in": "clock", "clk_out": {"clock_out": {"from": "clk_in", "relation": "derived"}}}}})
        dInstances = {"parameters": [], "ordered_parameters": 0, "ports": ["clk_in", "clk_out"], "ordered_ports": 0}
        self.assertEqual("module pll (input wire clk_in, output wire clk_out);\nendmodule\n", verilog_black_boxes.stub(oDesign, "pll", dInstances))


class test_cell_models(unittest.TestCase):
    """The black box libraries against the cell models of Yosys, when Yosys and its models are installed."""

    def setUp(self):
        sYosys = shutil.which("yosys")
        self.data = tools.data_directory(sYosys) if sYosys else None
        if self.data is None or not os.path.isdir(os.path.join(self.data, "xilinx")):
            self.skipTest("Yosys' cell models are not installed")

    def test_model_directions(self):
        # A declaration after a comma, as in output O, input I0, is read as such, not as a port named input
        with tempfile.TemporaryDirectory() as sDirectory:
            with open(os.path.join(sDirectory, "cells.v"), "w", encoding="utf-8") as oFile:
                oFile.write("module MUX(\n  (* clkbuf_driver *)\n  output O,\n  input I0, input I1,\n  input [1:0] S, T\n);\nendmodule\n")
            self.assertEqual(
                {"MUX": {"O": "output", "I0": "input", "I1": "input", "S": "input", "T": "input"}},
                verilog_black_boxes.model_directions(sDirectory, ["cells.v"], {"MUX"}),
            )

    def test_library_ports_exist(self):
        # Each port a library names, and each pattern, is a port of the primitive in the cell models
        lWrong = []
        for sLibrary, lFiles in verilog_black_boxes.YOSYS_MODELS.items():
            with open(os.path.join(black_box.BUILT_IN_DIRECTORY, f"{sLibrary}.yaml"), encoding="utf-8") as oFile:
                dTypes = yaml.safe_load(oFile).get("black_boxes") or {}
            dModels = {k.lower(): {s.lower() for s in v} for k, v in verilog_black_boxes.model_directions(self.data, lFiles, set(dTypes)).items()}
            for sType, dDeclaration in dTypes.items():
                setPorts = dModels.get(sType.lower())
                if setPorts is None:
                    continue
                lNames = list(dDeclaration.get("ports") or {})
                for dVariant in dDeclaration.get("variants") or []:
                    lNames += list(dVariant.get("ports") or {})
                for sName in lNames:
                    if not any(fnmatch.fnmatchcase(s, str(sName).lower()) for s in setPorts):
                        lWrong.append(f"{sLibrary} {sType} {sName}")
        self.assertEqual([], lWrong)
