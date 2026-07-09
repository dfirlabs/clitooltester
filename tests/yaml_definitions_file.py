#!/usr/bin/env python3
"""Tests for the YAML-based definition files."""

import unittest

from clitooltester import yaml_definitions_file

from tests import test_lib


class YAMLInputsDefinitionsFileTest(test_lib.BaseTestCase):
    """Tests for the YAML-based inputs file."""

    # pylint: disable=protected-access

    _TEST_YAML = {
        "name": "ext2",
        "path": "test_data/ext2.raw",
    }

    def testReadInputDefinition(self):
        """Tests the _ReadInputDefinition function."""
        test_definitions_file = yaml_definitions_file.YAMLInputsDefinitionsFile()

        definitions = test_definitions_file._ReadInputDefinition(self._TEST_YAML)

        self.assertIsNotNone(definitions)
        self.assertEqual(definitions.name, "ext2")
        self.assertEqual(
            definitions.path,
            "test_data/ext2.raw",
        )
        with self.assertRaises(RuntimeError):
            test_yaml = {}
            test_definitions_file._ReadInputDefinition(test_yaml)

        with self.assertRaises(RuntimeError):
            test_yaml = {"name": "ext2"}
            test_definitions_file._ReadInputDefinition(test_yaml)

        with self.assertRaises(RuntimeError):
            test_yaml = {"path": "test_data/ext2.raw"}
            test_definitions_file._ReadInputDefinition(test_yaml)

        with self.assertRaises(RuntimeError):
            test_yaml = {"bogus": "test"}
            test_definitions_file._ReadInputDefinition(test_yaml)

    def testReadFromFileObject(self):
        """Tests the _ReadFromFileObject function."""
        test_file_path = self._GetTestFilePath(["inputs.yaml"])
        self._SkipIfPathNotExists(test_file_path)

        test_definitions_file = yaml_definitions_file.YAMLInputsDefinitionsFile()

        with open(test_file_path, encoding="utf-8") as file_object:
            definitions = list(test_definitions_file._ReadFromFileObject(file_object))

        self.assertEqual(len(definitions), 1)

    def testReadFromFile(self):
        """Tests the ReadFromFile function."""
        test_file_path = self._GetTestFilePath(["inputs.yaml"])
        self._SkipIfPathNotExists(test_file_path)

        test_definitions_file = yaml_definitions_file.YAMLInputsDefinitionsFile()

        definitions = list(test_definitions_file.ReadFromFile(test_file_path))

        self.assertEqual(len(definitions), 1)

        self.assertEqual(definitions[0].name, "ext2")


class YAMLTestDefinitionFileTest(test_lib.BaseTestCase):
    """Tests for the YAML-based test definitions file."""

    # pylint: disable=protected-access

    _TEST_YAML = {
        "name": "dfimagetools_recursive_hasher",
        "command": "dfimagetools/scripts/recursive_hasher.py",
    }

    def testReadTestDefinition(self):
        """Tests the _ReadTestDefinition function."""
        test_definitions_file = yaml_definitions_file.YAMLTestDefinitionFile()

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
        test_file_path = self._GetTestFilePath(["test.yaml"])
        self._SkipIfPathNotExists(test_file_path)

        test_definitions_file = yaml_definitions_file.YAMLTestDefinitionFile()

        with open(test_file_path, encoding="utf-8") as file_object:
            definitions = list(test_definitions_file._ReadFromFileObject(file_object))

        self.assertEqual(len(definitions), 1)

    def testReadFromFile(self):
        """Tests the ReadFromFile function."""
        test_file_path = self._GetTestFilePath(["test.yaml"])
        self._SkipIfPathNotExists(test_file_path)

        test_definitions_file = yaml_definitions_file.YAMLTestDefinitionFile()

        definitions = list(test_definitions_file.ReadFromFile(test_file_path))

        self.assertEqual(len(definitions), 1)

        self.assertEqual(definitions[0].name, "dfimagetools_recursive_hasher")

    def testReadFromFileWithDocker(self):
        """Tests the ReadFromFile function on test that uses Docker."""
        test_file_path = self._GetTestFilePath(["test_with_docker.yaml"])
        self._SkipIfPathNotExists(test_file_path)

        test_definitions_file = yaml_definitions_file.YAMLTestDefinitionFile()

        definitions = list(test_definitions_file.ReadFromFile(test_file_path))

        self.assertEqual(len(definitions), 1)

        self.assertEqual(definitions[0].name, "dfimagetools_recursive_hasher_docker")


if __name__ == "__main__":
    unittest.main()
