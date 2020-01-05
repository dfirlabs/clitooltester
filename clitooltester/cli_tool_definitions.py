# -*- coding: utf-8 -*-
"""Command line tool definitions."""

from __future__ import unicode_literals

import sys

try:
  import ConfigParser as configparser
except ImportError:
  import configparser  # pylint: disable=import-error


class CLIToolDefinition(object):
  """Command line tool definition.

  Attributes:
    name (str): name that is used to reference to the tool within CLIToolTester.
    path (str): path of the command line tool.
  """

  def __init__(self, name):
    """Initializes a command line tool definition.

    Args:
      name (str): name of the command line tool.
    """
    super(CLIToolDefinition, self).__init__()
    self.name = name
    self.path = None


class CLIToolDefinitionReader(object):
  """Command line tool definition reader."""

  def _GetConfigValue(self, config_parser, section_name, value_name):
    """Retrieves a value from the config parser.

    Args:
      config_parser (ConfigParser): configuration parser.
      section_name (str): name of the section that contains the value.
      value_name (str): name of the value.

    Returns:
      object: value or None if the value does not exists.
    """
    try:
      return config_parser.get(section_name, value_name)
    except configparser.NoOptionError:
      return None

  def Read(self, file_object):
    """Reads command line tool definitions.

    Args:
      file_object (file): file-like object to read from.

    Yields:
      CLIToolDefinition: command line tool definition.
    """
    # TODO: replace by:
    # config_parser = configparser. ConfigParser(interpolation=None)
    config_parser = configparser.RawConfigParser()

    if sys.version_info[0] < 3:
      config_parser.readfp(file_object)  # pylint: disable=deprecated-method
    else:
      config_parser.read_file(file_object)

    for section_name in config_parser.sections():
      cli_tool_definition = CLIToolDefinition(section_name)

      cli_tool_definition.path = self._GetConfigValue(
          config_parser, section_name, 'path')

      yield cli_tool_definition
