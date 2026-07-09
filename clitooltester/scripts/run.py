#!/usr/bin/env python3
"""Script to run command line tool tests."""

import argparse
import logging
import sys

from clitooltester import test_runner


def Main():
    """Entry point of console script to run command line tool tests.

    Returns:
      int: exit code that is provided to sys.exit().
    """
    argument_parser = argparse.ArgumentParser(
        description="Runs command line tool tests."
    )
    argument_parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="enable debug output.",
    )
    argument_parser.add_argument(
        "-i",
        "--inputs",
        dest="inputs",
        action="store",
        default=None,
        help="path of the inputs configuration file.",
    )
    argument_parser.add_argument(
        "configuration",
        nargs="?",
        action="store",
        metavar="PATH",
        default=None,
        help="path of the test configuration file.",
    )
    options = argument_parser.parse_args()

    if not options.configuration:
        print("Test configuration file missing.")
        print("")
        argument_parser.print_help()
        print("")
        return 1

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    runner = test_runner.TestRunner()

    test_definition = runner.ReadTestConfiguration(options.configuration)
    if getattr(test_definition.package, "build"):
        exit_code = runner.BuildPackage(test_definition)
        if exit_code != 0:
            print("[ERROR] build failed")
            return 1

    result = 0
    if options.inputs:
        for input_definition in runner.ReadInputsConfiguration(options.inputs):
            exit_code = runner.RunTest(test_definition, test_input=input_definition)
            if exit_code != 0:
                print("[ERROR] test with input: {input_definition.path:s} failed")
                result = 1

    else:
        exit_code = runner.RunTest(test_definition)
        if exit_code != 0:
            print("[ERROR] test failed")
            result = 1

    return result


if __name__ == "__main__":
    sys.exit(Main())
