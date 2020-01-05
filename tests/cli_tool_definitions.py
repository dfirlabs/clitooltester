#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the command line tool definitions."""

from __future__ import unicode_literals

import io
import os
import unittest

from clitooltester import cli_tool_definitions

from tests import test_lib


class CLIToolDefinitionTest(test_lib.BaseTestCase):
  """Tests for the command line tool definition."""

  def testInitialize(self):
    """Tests the __init__ function."""
    test_definition = cli_tool_definitions.CLIToolDefinition('test')
    self.assertIsNotNone(test_definition)


class CLIToolDefinitionReaderTest(test_lib.BaseTestCase):
  """Tests for the command line tool definition reader."""

  # TODO: test _GetConfigValue function.

  def testRead(self):
    """Tests the Read function."""
    config_file = os.path.join('data', 'tools.ini')

    test_definitions = {}
    with io.open(config_file, 'r', encoding='utf-8') as file_object:
      test_definition_reader = cli_tool_definitions.CLIToolDefinitionReader()
      for test_definition in test_definition_reader.Read(file_object):
        test_definitions[test_definition.name] = test_definition

    self.assertGreaterEqual(len(test_definitions), 1)

    test_definition = test_definitions.get('dfvfs_recursive_hasher')
    self.assertIsNotNone(test_definition)

    self.assertEqual(test_definition.name, 'dfvfs_recursive_hasher')

    expected_path = 'dfvfs-snippets/scripts/recursive_hasher.py'
    self.assertEqual(test_definition.path, expected_path)


if __name__ == '__main__':
  unittest.main()
