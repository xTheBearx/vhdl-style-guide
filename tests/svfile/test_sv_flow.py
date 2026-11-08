# -*- coding: utf-8 -*-
"""The definite assignment walk of the rules that check variables read before they are assigned, see sv_flow."""

import unittest

from pyslang.syntax import SyntaxTree  # pylint: disable=import-error

import mhsg.svFile  # noqa: F401, pylint: disable=unused-import; loads the rules before the helpers they import
from mhsg.rules import sv_flow, sv_tree


def first_reads(sBody, setWatched):
    """The names of a block read before they are assigned, with the text of the first read."""
    oTree = SyntaxTree.fromText(f"module m; always_comb begin\n{sBody}\nend endmodule")
    oBlock = next(o for o in sv_tree.descendants(oTree.root) if o.kind.name == "AlwaysCombBlock")
    return {s: str(o).strip() for s, o in sv_flow.first_reads(oBlock.statement, set(setWatched)).items()}


class test_sv_flow(unittest.TestCase):
    def test_both_branches_assign(self):
        self.assertEqual({}, first_reads("if (a) t = 1; else t = 0; y = t;", "t"))

    def test_if_without_else(self):
        self.assertEqual({"t": "t"}, first_reads("if (a) t = 1; y = t;", "t"))

    def test_case_with_default(self):
        self.assertEqual({}, first_reads("case (s) 1: t = 1; default: t = 0; endcase y = t;", "t"))

    def test_case_without_default(self):
        self.assertEqual({"t": "t"}, first_reads("case (s) 1: t = 1; 2: t = 0; endcase y = t;", "t"))

    def test_unique_case_is_complete(self):
        self.assertEqual({}, first_reads("unique case (s) 1: t = 1; 2: t = 0; endcase y = t;", "t"))

    def test_loop_body_may_not_run(self):
        self.assertEqual({"t": "t"}, first_reads("for (int i = 0; i < n; i++) t = i; y = t;", "t"))

    def test_do_while_body_runs(self):
        self.assertEqual({}, first_reads("do t = 1; while (a); y = t;", "t"))

    def test_compound_assignment_reads(self):
        self.assertEqual({"k": "k"}, first_reads("k += 1;", "k"))

    def test_read_in_condition_and_index(self):
        self.assertEqual({"i": "i", "c": "c"}, first_reads("v[i] = 1; if (c) i = 0; i = 1; c = 0;", "ic"))

    def test_declaration_with_initializer(self):
        self.assertEqual({}, first_reads("logic t = a; y = t;", "t"))

    def test_function_name_is_not_read(self):
        self.assertEqual({}, first_reads("y = f(a); f = 1;", "f"))
