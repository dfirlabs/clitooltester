#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to run command line tool tests."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

from clitooltester import test_runner


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Runs command line tool tests.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'configuration', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the configuration file.')

  options = argument_parser.parse_args()

  if not options.configuration:
    print('Configuration file missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  runner = test_runner.TestRunner()

  runner.ReadConfiguration(options.configuration)

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
