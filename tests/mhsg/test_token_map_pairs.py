# -*- coding: utf-8 -*-
"""
Tests for matching start and end token indexes in token_map.
"""

import unittest

from mhsg import token_map


class test_extract_start_end_indexes(unittest.TestCase):
    def test_sequential_pairs(self):
        self.assertEqual(([1, 5], [3, 7]), token_map.extract_start_end_indexes([1, 5], [3, 7]))

    def test_nested_pairs(self):
        self.assertEqual(([1, 2, 4], [9, 3, 6]), token_map.extract_start_end_indexes([1, 2, 4], [3, 6, 9]))

    def test_unmatched_start_is_left_out(self):
        self.assertEqual(([2], [3]), token_map.extract_start_end_indexes([1, 2], [3]))

    def test_unmatched_end_is_left_out(self):
        self.assertEqual(([2], [4]), token_map.extract_start_end_indexes([2], [1, 4]))

    def test_start_and_end_at_the_same_index(self):
        self.assertEqual(([1, 3], [5, 3]), token_map.extract_start_end_indexes([1, 3], [3, 5]))

    def test_no_pairs(self):
        self.assertEqual(([], []), token_map.extract_start_end_indexes([5], [1]))

    def test_arguments_are_not_changed(self):
        lStarts = [1, 2]
        lEnds = [3, 4]
        token_map.extract_start_end_indexes(lStarts, lEnds)
        self.assertEqual([1, 2], lStarts)
        self.assertEqual([3, 4], lEnds)

    def test_many_pairs(self):
        # Matching used to take quadratic time in the number of pairs
        iCount = 200000
        lStarts = list(range(0, 2 * iCount, 2))
        lEnds = list(range(1, 2 * iCount, 2))
        self.assertEqual((lStarts, lEnds), token_map.extract_start_end_indexes(lStarts, lEnds))
