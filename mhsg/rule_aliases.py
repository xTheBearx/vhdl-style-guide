# -*- coding: utf-8 -*-

import os

import yaml

from mhsg import exceptions

with open(os.path.join(os.path.dirname(__file__), "rule_aliases.yaml"), encoding="utf-8") as oFile:
    dAliases = yaml.safe_load(oFile)

dRuleIds = {sAlias: sRuleId for sRuleId, sAlias in dAliases.items()}


def get_alias(sRuleId):
    """
    Returns the alias of a rule, or None if the rule has no alias.
    """
    return dAliases.get(sRuleId)


def get_rule_id(sName):
    """
    Returns the rule identifier for an alias, or the name unchanged if it is not an alias.
    """
    return dRuleIds.get(sName, sName)


def resolve_rule_configuration(dRuleConfiguration, sConfigFilename):
    """
    Replaces aliases with rule identifiers in the rule section of a configuration.
    """
    if not isinstance(dRuleConfiguration, dict):
        return dRuleConfiguration
    dReturn = {}
    for sName, dValue in dRuleConfiguration.items():
        sRuleId = get_rule_id(sName)
        if sRuleId != sName and sRuleId in dRuleConfiguration:
            raise exceptions.ConfigurationError(
                f"ERROR: configuration file {sConfigFilename}: rule {sRuleId} is configured with both its identifier and its alias {sName}.",
            )
        dReturn[sRuleId] = dValue
    return dReturn
