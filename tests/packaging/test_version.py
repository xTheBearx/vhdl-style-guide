# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import unittest

sRoot = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@unittest.skipUnless(shutil.which("git") and os.path.isdir(os.path.join(sRoot, ".git")), "not a git checkout")
class test_version(unittest.TestCase):
    def test_uv_marker_is_ignored(self):
        # uv writes .ok into its git checkouts; setuptools-git-versioning counts any untracked file as a change,
        # so an install from a tag would read 4.0.2.post0+git.<sha>.dirty
        oResult = subprocess.run(["git", "check-ignore", "-q", ".ok"], cwd=sRoot, check=False)
        self.assertEqual(oResult.returncode, 0)
