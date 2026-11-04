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


class VerilogDesign(Design):
    def __init__(self, dBlackBoxes, lFiles):
        super().__init__(dBlackBoxes)
        self.files = lFiles
        self.defines = {}
        self.include_directories = []

    def verilog_files(self):
        return self.files


class test_slang_stubs(unittest.TestCase):
    """read_slang connects only nets to inout ports: the stubs give each port a direction where they can."""

    def test_directions_from_connections_and_suffixes(self):
        with tempfile.TemporaryDirectory() as sDirectory:
            sFile = os.path.join(sDirectory, "top.sv")
            with open(sFile, "w", encoding="utf-8") as oFile:
                oFile.write(
                    "module top (input logic clk, input logic a, output logic q);\n"
                    "  logic irq, r;\n"
                    "  always_ff @(posedge clk) r <= a;\n"
                    "  vendor_ip u_ip (.aclk(clk), .data(r), .irq(irq), .cfg(1'b0), .status_o(), .ready_i(q));\n"
                    "  assign q = irq;\n"
                    "endmodule\n",
                )
            oDesign = VerilogDesign({}, [sFile])
            dDirections = verilog_black_boxes.connection_directions(oDesign, {"vendor_ip"})
            # An input of the module, a signal it assigns and a constant are inputs; a signal nothing drives is an output.
            # q is assigned, so ready_i is an input; status_o connects nothing and is left out
            self.assertEqual({"aclk": "input", "data": "input", "irq": "output", "cfg": "input", "ready_i": "input"}, dDirections["vendor_ip"])
            dInstances = {"parameters": [], "ordered_parameters": 0, "ports": ["aclk", "data", "irq", "cfg", "status_o", "spare"], "ordered_ports": 0}
            dInstances["connected"] = dDirections["vendor_ip"]
            self.assertEqual(
                "(* mhsg_inferred_directions *) module vendor_ip "
                "(input wire aclk, input wire data, output wire irq, input wire cfg, output wire status_o, inout wire spare);\nendmodule\n",
                verilog_black_boxes.stub(oDesign, "vendor_ip", dInstances, bSlang=True),
            )

    def test_suffixes(self):
        self.assertEqual(
            ["input", "input", "output", "output", "inout"],
            [verilog_black_boxes.suffix_direction(s) for s in ("clk_i", "rst_ni", "data_o", "valid_no", "pad")],
        )


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
