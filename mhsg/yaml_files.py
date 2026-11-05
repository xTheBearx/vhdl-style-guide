# -*- coding: utf-8 -*-
"""
Reading YAML with the loaders written in C when PyYAML has them, which are several times faster than those written in
Python: mhsg reads its rule aliases, option catalog, styles and rule sets at every start. A file with a mistake is read
again with the loader written in Python, whose message about the mistake is the one reported, as it always was.
"""

import io

import yaml

SAFE_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
FULL_LOADER = getattr(yaml, "CFullLoader", yaml.FullLoader)


def load(oStream, oFast, oSlow):
    sText = oStream.read() if hasattr(oStream, "read") else oStream
    try:
        return yaml.load(sText, Loader=oFast)  # noqa: S506 - the safe or full loader
    except yaml.YAMLError:
        if oFast is oSlow:
            raise
        # A stream named as the file, which the message names
        oText = io.StringIO(sText)
        oText.name = getattr(oStream, "name", "<unicode string>")
        return yaml.load(oText, Loader=oSlow)  # noqa: S506 - the safe or full loader


def safe_load(oStream):
    """As yaml.safe_load."""
    return load(oStream, SAFE_LOADER, yaml.SafeLoader)


def full_load(oStream):
    """As yaml.full_load."""
    return load(oStream, FULL_LOADER, yaml.FullLoader)
