# -*- coding: utf-8 -*-
import functools
import json
import multiprocessing
import os
import sys

from mhsg.report import quality_report
from mhsg.svFile import project as sv_project

from . import (
    apply_rules,
    cmd_line_args,
    config,
    exceptions,
    junit,
    options_description,
    project_index,
    provenance,
    rule_list,
    rule_set,
    utils,
    version,
    vhdlFile,
)


def generate_output_configuration(commandLineArguments, oConfig):
    """
    Creates a configuration based on parameters passed on the command line.
    It will send the output to a file in JSON format.

    Parameters:

      commandLineArguments: (argparse object)

      configuration: (configuration dictionary)

    Returns:  Nothing
    """
    if commandLineArguments.output_configuration:
        configuration = oConfig.dConfig
        fExitStatus = 0
        # Create empty file so it can be used to create the rule list
        oVhdlFile = vhdlFile.vhdlFile([""])
        oRules = rule_list.rule_list(oVhdlFile, oConfig.severity_list, commandLineArguments.local_rules, bAllLanguages=True)
        rule_set.apply(oRules, oConfig)
        oRules.configure(oConfig)
        dOutputConfiguration = {}
        if commandLineArguments.filename:
            dOutputConfiguration["file_list"] = []
            for sFileName in commandLineArguments.filename:
                dOutputConfiguration["file_list"].append(sFileName)
        if commandLineArguments.local_rules:
            dOutputConfiguration["local_rules"] = commandLineArguments.local_rules
        dOutputConfiguration["rule"] = oRules.get_configuration()
        dOutputConfiguration["indent"] = configuration["indent"]
        dOutputConfiguration["pragma"] = {}
        dOutputConfiguration["pragma"]["patterns"] = configuration["pragma"]["patterns"]
        with open(commandLineArguments.output_configuration, "w", encoding="utf-8") as json_file:
            json.dump(dOutputConfiguration, json_file, sort_keys=True, indent=2)
        sys.exit(fExitStatus)


def generate_options_description(commandLineArguments):
    """
    Writes a description of every option to the file given with --output_options and exits.
    """
    if commandLineArguments.output_options:
        options_description.write(commandLineArguments.output_options, commandLineArguments.local_rules)
        sys.exit(0)


def run_design_analysis(commandLineArguments, oConfig):
    """Runs design analysis on the design in the configuration, prints its report and exits."""
    from mhsg.design import analysis

    for sDirectory in config.get_local_rule_directories(commandLineArguments.local_rules):
        sys.path.append(os.path.abspath(sDirectory))
    try:
        sys.exit(analysis.run(commandLineArguments, oConfig))
    except (exceptions.ConfigurationError, exceptions.DesignError) as e:
        print(e.message)
        sys.exit(1)


def display_rule_configuration(commandLineArguments, oConfig):
    """
    Displays the configuration of a rule passed on the command line.

    Parameters:

      commandLineArguments: (argparse object)

      configuration: (configuration dictionary)

    Returns:  Nothing
    """
    if commandLineArguments.rule_configuration:
        fExitStatus = 0
        # Create empty file so it can be used to create the rule list
        oVhdlFile = vhdlFile.vhdlFile([""])
        oRules = rule_list.rule_list(oVhdlFile, oConfig.severity_list, commandLineArguments.local_rules, bAllLanguages=True)
        rule_set.apply(oRules, oConfig)
        oRules.configure(oConfig)
        dOutputConfiguration = {}
        if commandLineArguments.local_rules:
            dOutputConfiguration["local_rules"] = commandLineArguments.local_rules
        dFullConfiguration = oRules.get_configuration()
        # The rule can be given by its identifier or its alias
        dAliases = {oRule.alias: oRule.unique_id for oRule in oRules.rules if oRule.alias is not None}
        sRuleId = dAliases.get(commandLineArguments.rule_configuration, commandLineArguments.rule_configuration)
        if sRuleId in dFullConfiguration:
            dOutputConfiguration["rule"] = {}
            dOutputConfiguration["rule"][sRuleId] = {}
            sAlias = rule_list.get_rule_alias(oRules, sRuleId)
            if sAlias is not None:
                dOutputConfiguration["rule"][sRuleId]["alias"] = sAlias
            dOutputConfiguration["rule"][sRuleId].update(dFullConfiguration[sRuleId])
            # Format the data for displaying
            print(json.dumps(dOutputConfiguration, indent=2))
        else:
            print("ERROR: rule " + commandLineArguments.rule_configuration + " was not found.")
            fExitStatus = 1
        sys.exit(fExitStatus)


def validate_stdout_option(commandLineArguments):
    if not commandLineArguments.stdout:
        return
    if not commandLineArguments.fix:
        print("ERROR: --stdout requires --fix", file=sys.stderr)
        sys.exit(1)
    iInputs = int(commandLineArguments.stdin) + (
        0 if commandLineArguments.stdin or commandLineArguments.filename is None else len(commandLineArguments.filename)
    )
    if iInputs != 1:
        print("ERROR: --stdout requires a single input file or --stdin", file=sys.stderr)
        sys.exit(1)


def validate_files_exist_to_analyze(sName, stdin):
    if sName is None and not stdin:
        print("ERROR: No file defined by the -f command line option or filename given in configuration file.")
        sys.exit(1)


def get_index_files(commandLineArguments):
    """
    Returns the files read for the project index: the analyzed files, and the
    files given with --index_files or index_file_list, which are not analyzed.
    """
    lReturn = list(commandLineArguments.filename or [])
    for sPattern in getattr(commandLineArguments, "index_files", None) or []:
        for sFilename in config.glob_filenames(sPattern) or [sPattern]:
            if sFilename not in lReturn:
                lReturn.append(sFilename)
    return lReturn


def main():
    """Main routine of the Multiple HDL Style Guide (MHSG) program."""

    fExitStatus = 0

    commandLineArguments = cmd_line_args.parse_command_line_arguments()

    version.print_version(commandLineArguments)

    oConfig = config.New(commandLineArguments)
    try:
        rule_set.configure_lint_mode(oConfig, commandLineArguments)
    except exceptions.ConfigurationError as e:
        print(e.message)
        sys.exit(1)

    if commandLineArguments.design:
        run_design_analysis(commandLineArguments, oConfig)
    if not commandLineArguments.stdin:
        lIndexFiles = get_index_files(commandLineArguments)
        oConfig.project_type_names = project_index.collect_type_names(lIndexFiles)
        oConfig.project_positional_entities = project_index.collect_positional_entity_instantiations(lIndexFiles)
        oConfig.project_port_orders = project_index.collect_port_orders(lIndexFiles)
        if oConfig.lint_mode is not None:
            oConfig.project_port_modes = project_index.collect_port_modes(lIndexFiles)
            # The SystemVerilog files of the run are compiled together once, see svFile/project.py
            oConfig.sv_lint_project = sv_project.collect(lIndexFiles, oConfig.dConfig, sv_project.verilator_enabled(oConfig))
        oConfig.project_positional_generic_entities = project_index.collect_positional_entity_instantiations(lIndexFiles, "generic")

    # Add local rule path to system path so the rules can be loaded
    for sDirectory in config.get_local_rule_directories(commandLineArguments.local_rules):
        sys.path.append(os.path.abspath(sDirectory))

    if commandLineArguments.junit:
        oJunitFile = junit.xmlfile(commandLineArguments.junit)
        oJunitTestsuite = junit.testsuite("vhdl-style-guide", str(0))
        for sName, sValue in provenance.properties(provenance.record(commandLineArguments, oConfig)):
            oJunitTestsuite.add_property(sName, sValue)

    generate_output_configuration(commandLineArguments, oConfig)

    generate_options_description(commandLineArguments)

    display_rule_configuration(commandLineArguments, oConfig)

    dJson = create_json_dictionary()
    if commandLineArguments.json:
        dJson["run"] = provenance.record(commandLineArguments, oConfig)

    f = functools.partial(apply_rules.apply_rules, commandLineArguments, oConfig)
    # It's easier to debug when not using multiprocessing.Pool()
    lReturn = []
    validate_stdout_option(commandLineArguments)
    if commandLineArguments.jobs == 1 or commandLineArguments.stdin or commandLineArguments.stdout:
        validate_files_exist_to_analyze(commandLineArguments.filename, commandLineArguments.stdin)
        if commandLineArguments.stdin:
            fStatus, testCase, dJsonEntry, sOutputStd, sOutputErr, bKeepProcessingFiles = f((0, "stdin"))
            lReturn.append((fStatus, testCase, dJsonEntry))
            if sOutputStd:
                print(sOutputStd)
            if sOutputErr:
                print(sOutputErr, file=sys.stderr)

        else:
            for iIndex, sFileName in enumerate(commandLineArguments.filename):
                fStatus, testCase, dJsonEntry, sOutputStd, sOutputErr, bKeepProcessingFiles = f((iIndex + int(commandLineArguments.stdin), sFileName))
                lReturn.append((fStatus, testCase, dJsonEntry))
                if sOutputStd:
                    print(sOutputStd)
                if sOutputErr:
                    print(sOutputErr, file=sys.stderr)
                if bKeepProcessingFiles:
                    break

    else:
        validate_files_exist_to_analyze(commandLineArguments.filename, False)
        with multiprocessing.Pool(commandLineArguments.jobs) as pool:
            for tResult in pool.imap(f, enumerate(commandLineArguments.filename)):
                fStatus, testCase, dJsonEntry, sOutputStd, sOutputErr, bKeepProcessingFiles = tResult
                lReturn.append((fStatus, testCase, dJsonEntry))
                if sOutputStd:
                    print(sOutputStd)
                if sOutputErr:
                    print(sOutputErr, file=sys.stderr)
                if bKeepProcessingFiles:
                    break

    for tValue in lReturn:
        fStatus, testCase, dJsonEntry = tValue
        fExitStatus = fExitStatus or fStatus

        if commandLineArguments.junit:
            oJunitTestsuite.add_testcase(testCase)

        if commandLineArguments.json or commandLineArguments.quality_report:
            dJson["files"].append(dJsonEntry)

    if commandLineArguments.junit:
        oJunitFile.add_testsuite(oJunitTestsuite)
        utils.write_junit_xml_file(oJunitFile)

    if commandLineArguments.json:
        with open(commandLineArguments.json, "w", encoding="utf-8") as oFile:
            oFile.write(json.dumps(dJson, indent=2))

    if commandLineArguments.quality_report:
        quality_report.write(commandLineArguments, dJson)

    sys.exit(fExitStatus)


def create_json_dictionary():
    """
    Returns a dictionary to be used when the --json option is chosen.
    """
    dJson = {}
    dJson["files"] = []
    return dJson
