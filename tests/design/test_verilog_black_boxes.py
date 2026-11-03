# -*- coding: utf-8 -*-
"""The modules a Verilog design instantiates but no file defines, see mhsg/design/verilog_black_boxes.py."""

import unittest

from mhsg.design import black_box, verilog_black_boxes


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
