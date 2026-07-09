#!/usr/bin/env python3
"""Script to run command line tool tests."""

import argparse
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

    runner = test_runner.TestRunner()

    try:
        test_definition = runner.ReadTestConfiguration(options.configuration)
    except (FileNotFoundError, IOError, RuntimeError) as exception:
        print(
            f"Unable to read test configuration file: '{options.configuration:s}' "
            f"with error: {exception!s}"
        )
        return 1

    if test_definition.package and getattr(test_definition.package, "build"):
        if runner.BuildPackage(test_definition) != 0:
            print("\033[31mERROR: build failed\033[0m")
            return 1

    if test_definition.docker and getattr(test_definition.docker, "dockerfile"):
        if runner.BuildDockerImage(test_definition) != 0:
            print("\033[31mERROR: docker build failed\033[0m")
            return 1

    number_of_tests = 0
    number_of_failed_tests = 0

    if not options.inputs:
        if runner.RunTest(test_definition) != 0:
            number_of_failed_tests += 1

        number_of_tests += 1
    else:
        for input_definition in runner.ReadInputsConfiguration(options.inputs):
            if runner.RunTest(test_definition, test_input=input_definition) != 0:
                number_of_failed_tests += 1

            number_of_tests += 1

    print("\nTest results.\n")

    if number_of_failed_tests != 0:
        if number_of_tests == 1:
            print(
                f"\033[31mERROR: 1 test was run,\n{number_of_failed_tests:d} failed "
                f"unexpectedly.\033[0m"
            )
        else:
            print(
                f"\033[31mERROR: All {number_of_tests:d} tests were run,\n"
                f"{number_of_failed_tests:d} failed unexpectedly.\033[0m"
            )
        return 1

    if number_of_tests == 1:
        print("\033[32m1 test was successful.\033[0m")
    else:
        print(f"\033[32mAll {number_of_tests:d} tests were successful.\033[0m")

    return 0


if __name__ == "__main__":
    sys.exit(Main())
