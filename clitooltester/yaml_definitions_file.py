"""YAML-based definitions files."""

import yaml

from clitooltester import resources


class YAMLTestsDefinitionsFile:
    """YAML-based tests definitions file.

    A YAML-based tests definitions file contains one or more test definitions. A test
    definition consists of:

    name: plaso_log2timeline_with_image.qcow2
    command: log2timeline.py unattended %input%

    Where:
    * name, that uniquely identifies the test;
    * command, with arguments, with can consist of placeholder values, such as: %input%.
    """

    _SUPPORTED_KEYS = frozenset(["command", "name"])

    def _ReadTestDefinition(self, yaml_test_definition):
        """Reads a test definition from a dictionary.

        Args:
          yaml_test_definition (dict[str, object]): YAML test definition values.

        Returns:
          TestDefinition: test definition.

        Raises:
          RuntimeError: if the format of the formatter definition is not set
              or incorrect.
        """
        if not yaml_test_definition:
            raise RuntimeError("Missing test definition values.")

        different_keys = set(yaml_test_definition) - self._SUPPORTED_KEYS
        if different_keys:
            different_keys = ", ".join(different_keys)
            raise RuntimeError(f"Undefined keys: {different_keys:s}")

        command = yaml_test_definition.get("command")
        if not command:
            raise RuntimeError("Invalid test definition missing command.")

        name = yaml_test_definition.get("name")
        if not name:
            raise RuntimeError("Invalid test definition missing name.")

        test_definition = resources.TestDefinition()
        test_definition.command = command
        test_definition.name = name

        return test_definition

    def _ReadFromFileObject(self, file_object):
        """Reads the event formatters from a file-like object.

        Args:
          file_object (file): formatters file-like object.

        Yields:
          TestDefinition: test definition.
        """
        yaml_generator = yaml.safe_load_all(file_object)

        for yaml_test_definition in yaml_generator:
            yield self._ReadTestDefinition(yaml_test_definition)

    def ReadFromFile(self, path):
        """Reads the event formatters from a YAML file.

        Args:
          path (str): path to a formatters file.

        Yields:
          TestDefinition: test definition.
        """
        with open(path, encoding="utf-8") as file_object:
            yield from self._ReadFromFileObject(file_object)
