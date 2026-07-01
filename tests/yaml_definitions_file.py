#!/usr/bin/env python3
"""Tests for the YAML-based test definitions file."""

import unittest

from clitooltester import yaml_definitions_file

from tests import test_lib


class YAMLTestDefinitionsFileTest(test_lib.BaseTestCase):
    """Tests for the YAML-based test definitions file."""

    # pylint: disable=protected-access

    _TEST_YAML = {
        "name": "dfimagetools_recursive_hasher",
        "command": "dfimagetools/scripts/recursive_hasher.py",
    }

    def testReadTestDefinition(self):
        """Tests the _ReadTestDefinition function."""
        test_definitions_file = yaml_definitions_file.YAMLTestsDefinitionsFile()

        definitions = test_definitions_file._ReadTestDefinition(self._TEST_YAML)

        self.assertIsNotNone(definitions)
        self.assertEqual(definitions.name, "dfimagetools_recursive_hasher")
        self.assertEqual(
            definitions.command,
            "dfimagetools/scripts/recursive_hasher.py",
        )

        with self.assertRaises(RuntimeError):
            test_yaml = {}
            test_definitions_file._ReadTestDefinition(test_yaml)

        with self.assertRaises(RuntimeError):
            test_yaml = {"name": "dfimagetools_recursive_hasher"}
            test_definitions_file._ReadTestDefinition(test_yaml)

        with self.assertRaises(RuntimeError):
            test_yaml = {"command": "dfimagetools/scripts/recursive_hasher.py"}
            test_definitions_file._ReadTestDefinition(test_yaml)

        with self.assertRaises(RuntimeError):
            test_yaml = {"bogus": "test"}
            test_definitions_file._ReadTestDefinition(test_yaml)

    def testReadFromFileObject(self):
        """Tests the _ReadFromFileObject function."""
        test_file_path = self._GetTestFilePath(["tests.yaml"])
        self._SkipIfPathNotExists(test_file_path)

        test_definitions_file = yaml_definitions_file.YAMLTestsDefinitionsFile()

        with open(test_file_path, encoding="utf-8") as file_object:
            definitions = list(test_definitions_file._ReadFromFileObject(file_object))

        self.assertEqual(len(definitions), 1)

    def testReadFromFile(self):
        """Tests the ReadFromFile function."""
        test_file_path = self._GetTestFilePath(["tests.yaml"])
        self._SkipIfPathNotExists(test_file_path)

        test_definitions_file = yaml_definitions_file.YAMLTestsDefinitionsFile()

        definitions = list(test_definitions_file.ReadFromFile(test_file_path))

        self.assertEqual(len(definitions), 1)

        self.assertEqual(definitions[0].name, "dfimagetools_recursive_hasher")


if __name__ == "__main__":
    unittest.main()
