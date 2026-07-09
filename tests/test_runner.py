#!/usr/bin/env python3
"""Tests of the command line tool test runner."""

import os
import tempfile
import unittest

from unittest import mock

from clitooltester import resources
from clitooltester import test_runner

from tests import test_lib


class TestRunnerTest(test_lib.BaseTestCase):
    """Tests the command line tool test runner."""

    # pylint: disable=protected-access

    def testSubstituteInputPlaceholder(self):
        """Tests the _SubstitutePlaceholders function."""
        # Test with %input%
        runner = test_runner.TestRunner()
        command = "%input%"
        test_values = {"%input%": "/input/test.raw"}

        result = runner._SubstitutePlaceholders(command, test_values)
        self.assertEqual(result, "/input/test.raw")

        # Test with %package%
        runner = test_runner.TestRunner()
        command = "%package%/scripts/analyze.py"
        test_values = {"%package%": "/home/user/pkg"}

        result = runner._SubstitutePlaceholders(command, test_values)
        self.assertEqual(result, "/home/user/pkg/scripts/analyze.py")

        # Test with %input% and %package%
        runner = test_runner.TestRunner()
        command = "%package%/tool %input%"
        test_values = {"%package%": "/home/user/pkg", "%input%": "/input/data"}

        result = runner._SubstitutePlaceholders(command, test_values)
        self.assertEqual(result, "/home/user/pkg/tool /input/data")

        # Test without placeholders
        runner = test_runner.TestRunner()
        command = "ls -la"
        test_values = {}

        result = runner._SubstitutePlaceholders(command, test_values)
        self.assertEqual(result, "ls -la")

        # Test with unsupported placeholder
        runner = test_runner.TestRunner()
        command = "%input%/other.txt"
        test_values = {"%in%": "partial"}

        result = runner._SubstitutePlaceholders(command, test_values)
        self.assertEqual(result, "%input%/other.txt")

        # Test with multiple occurrences of %input%
        runner = test_runner.TestRunner()
        command = "%input% and %input%"
        test_values = {"%input%": "/path"}

        result = runner._SubstitutePlaceholders(command, test_values)
        self.assertEqual(result, "/path and /path")

    @mock.patch("clitooltester.test_runner.subprocess.run")
    def testRunTestWithDocker(self, mock_subprocess_run):
        """Tests the _RunTestWithDocker function."""
        # Test with subprocess.run success
        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        docker = resources.DockerDefinition()
        docker.tag = "myimage:latest"

        test_definition = resources.TestDefinition()
        test_definition.name = "my_test"
        test_definition.command = "ls /input"
        test_definition.docker = docker

        result = runner._RunTestWithDocker(test_definition, silent=True)
        self.assertEqual(result, 0)

        # Test with input and subprocess.run success
        mock_subprocess_run.reset_mock()

        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        docker = resources.DockerDefinition()
        docker.tag = "myimage:latest"

        test_definition = resources.TestDefinition()
        test_definition.name = "my_test"
        test_definition.command = "ls %input%"
        test_definition.docker = docker

        test_input = resources.InputDefinition()
        test_input.name = "test_input"
        test_input.path = "/some/path/data.bin"

        result = runner._RunTestWithDocker(
            test_definition, silent=True, test_input=test_input
        )
        self.assertEqual(result, 0)

        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args[0][0]
        self.assertIn("-v", call_args)
        self.assertIn("/input/data.bin", " ".join(call_args))

        # Test with input set and subprocess.run success
        mock_subprocess_run.reset_mock()

        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        docker = resources.DockerDefinition()
        docker.tag = "myimage:latest"

        test_definition = resources.TestDefinition()
        test_definition.name = "my_test"
        test_definition.command = "ls %input%"
        test_definition.docker = docker

        test_input = resources.InputDefinition()
        test_input.name = "ext/ext2"
        test_input.path = "/mnt/hdd/test_data/ext/ext2.raw"

        result = runner._RunTestWithDocker(
            test_definition, silent=True, test_input=test_input
        )
        self.assertEqual(result, 0)

        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args[0][0]
        self.assertIn("-v", call_args)
        self.assertIn("ext2.raw", " ".join(call_args))

        # Test with missing configuration
        mock_subprocess_run.reset_mock()

        runner = test_runner.TestRunner()
        test_definition = resources.TestDefinition()
        test_definition.name = "test"
        test_definition.command = "mycommand"
        test_definition.docker = None

        with self.assertRaises(ValueError):
            runner._RunTestWithDocker(test_definition, silent=True)

        # Test with subprocess.run failure
        mock_subprocess_run.reset_mock()

        mock_result = mock.MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "stdout output\n"
        mock_result.stderr = "stderr output\n"
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        docker = resources.DockerDefinition()
        docker.tag = "myimage:latest"

        test_definition = resources.TestDefinition()
        test_definition.name = "my_test"
        test_definition.command = "ls /input"
        test_definition.docker = docker

        result = runner._RunTestWithDocker(test_definition, silent=True)
        self.assertEqual(result, 1)

    @mock.patch("clitooltester.test_runner.subprocess.run")
    def testRunTestWithPackageSuccess(self, mock_subprocess_run):
        """Tests the _RunTestWithPackage function."""
        # Test with subprocess.run success
        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        package = resources.PackageDefinition()
        package.path = "/home/user/pkg"

        test_definition = resources.TestDefinition()
        test_definition.name = "my_test"
        test_definition.command = "%package%/tool"
        test_definition.package = package

        result = runner._RunTestWithPackage(test_definition, silent=True)
        self.assertEqual(result, 0)

        # Test with input and subprocess.run success
        mock_subprocess_run.reset_mock()

        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        package = resources.PackageDefinition()
        package.path = "/home/user/pkg"

        test_definition = resources.TestDefinition()
        test_definition.name = "my_test"
        test_definition.command = "%package%/tool %input%"
        test_definition.package = package

        test_input = resources.InputDefinition()
        test_input.name = "data"
        test_input.path = "/data/file.bin"

        result = runner._RunTestWithPackage(
            test_definition, silent=True, test_input=test_input
        )
        self.assertEqual(result, 0)

        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args[0][0]
        self.assertIn("/data/file.bin", call_args[0])

        # TODO: Test with input set and subprocess.run success

        # Test with missing configuration
        mock_subprocess_run.reset_mock()

        runner = test_runner.TestRunner()
        test_definition = resources.TestDefinition()
        test_definition.name = "test"
        test_definition.command = "mycommand"
        test_definition.package = None

        with self.assertRaises(ValueError):
            runner._RunTestWithPackage(test_definition, silent=True)

        # Test with subprocess.run failure
        mock_subprocess_run.reset_mock()

        mock_result = mock.MagicMock()
        mock_result.returncode = 2
        mock_result.stdout = "stdout output\n"
        mock_result.stderr = "stderr output\n"
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        package = resources.PackageDefinition()
        package.path = "/home/user/pkg"

        test_definition = resources.TestDefinition()
        test_definition.name = "my_test"
        test_definition.command = "command"
        test_definition.package = package

        result = runner._RunTestWithPackage(test_definition, silent=True)
        self.assertEqual(result, 2)

    @mock.patch("clitooltester.test_runner.subprocess.run")
    @mock.patch("clitooltester.test_runner.os.environ")
    def testBuildPackage(self, mock_environ, mock_subprocess_run):
        """Tests the BuildPackage function."""
        # Test with subprocess.run success
        mock_environ.get.return_value = "/bin/bash"
        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        package = resources.PackageDefinition()
        package.path = "/home/user/pkg"
        package.build = "make install"
        package.build_env = None
        test_definition = resources.TestDefinition()
        test_definition.package = package

        result = runner.BuildPackage(test_definition, silent=True)
        self.assertEqual(result, 0)

        # Test with build_env and subprocess.run success
        mock_subprocess_run.reset_mock()

        mock_environ.get.return_value = "/bin/sh"
        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        package = resources.PackageDefinition()
        package.path = "/home/user/pkg"
        package.build = "build.sh"
        package.build_env = {"CC": "clang"}
        test_definition = resources.TestDefinition()
        test_definition.package = package

        result = runner.BuildPackage(test_definition, silent=True)
        self.assertEqual(result, 0)

        mock_subprocess_run.assert_called_once()
        call_kwargs = mock_subprocess_run.call_args[1]
        self.assertEqual(call_kwargs["env"]["CC"], "clang")
        self.assertEqual(call_kwargs["cwd"], "/home/user/pkg")

        # Test with missing configuration
        mock_subprocess_run.reset_mock()

        runner = test_runner.TestRunner()
        test_definition = resources.TestDefinition()
        test_definition.package = None

        with self.assertRaises(ValueError):
            runner.BuildPackage(test_definition, silent=True)

        # Test with subprocess.run failure
        mock_subprocess_run.reset_mock()

        mock_environ.get.return_value = "/bin/bash"
        mock_result = mock.MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "build stdout\n"
        mock_result.stderr = "build stderr\n"
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        package = resources.PackageDefinition()
        package.path = "/home/user/pkg"
        package.build = "make install"
        package.build_env = None
        test_definition = resources.TestDefinition()
        test_definition.package = package

        result = runner.BuildPackage(test_definition, silent=True)
        self.assertEqual(result, 1)

    @mock.patch("clitooltester.test_runner.subprocess.run")
    def testBuildDocker(self, mock_subprocess_run):
        """Tests the BuildDockerImage function."""
        # Test with subprocess.run success
        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        docker = resources.DockerDefinition()
        docker.tag = "myimage:latest"
        docker.dockerfile = "Dockerfile"

        test_definition = resources.TestDefinition()
        test_definition.docker = docker

        result = runner.BuildDockerImage(test_definition, silent=True)
        self.assertEqual(result, 0)

        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args[0][0]
        self.assertIn("myimage:latest", call_args)
        self.assertIn("Dockerfile", call_args)

        # Test with subprocess.run failure
        mock_subprocess_run.reset_mock()

        mock_result = mock.MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "docker stdout\n"
        mock_result.stderr = "docker stderr\n"
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        docker = resources.DockerDefinition()
        docker.tag = "myimage:latest"
        docker.dockerfile = "Dockerfile"

        test_definition = resources.TestDefinition()
        test_definition.docker = docker

        result = runner.BuildDockerImage(test_definition, silent=True)
        self.assertEqual(result, 1)

        # Test with missing configuration
        mock_subprocess_run.reset_mock()

        runner = test_runner.TestRunner()
        test_definition = resources.TestDefinition()
        test_definition.docker = None

        with self.assertRaises(ValueError):
            runner.BuildDockerImage(test_definition, silent=True)

        # Test with missing dockerfile
        mock_subprocess_run.reset_mock()

        runner = test_runner.TestRunner()
        docker = resources.DockerDefinition()
        docker.tag = "myimage:latest"
        docker.dockerfile = None

        test_definition = resources.TestDefinition()
        test_definition.docker = docker

        with self.assertRaises(ValueError):
            runner.BuildDockerImage(test_definition, silent=True)

    def testReadInputsConfiguration(self):
        """Tests the ReadInputsConfiguration function."""
        test_file_path = self._GetTestFilePath(["inputs.yaml"])
        self._SkipIfPathNotExists(test_file_path)

        runner = test_runner.TestRunner()
        inputs = runner.ReadInputsConfiguration(test_file_path)

        self.assertEqual(len(inputs), 1)
        self.assertEqual(inputs[0].name, "ext2")

        # Test with input set
        test_file_path = self._GetTestFilePath(["inputs_with_set.yaml"])
        self._SkipIfPathNotExists(test_file_path)

        runner = test_runner.TestRunner()
        inputs = runner.ReadInputsConfiguration(test_file_path)

        self.assertEqual(len(inputs), 1)
        self.assertEqual(inputs[0].name, "ext/ext2")

    def testReadTestConfiguration(self):
        """Tests the ReadTestConfiguration function."""
        test_file_path = self._GetTestFilePath(["test.yaml"])
        self._SkipIfPathNotExists(test_file_path)

        runner = test_runner.TestRunner()
        result = runner.ReadTestConfiguration(test_file_path)

        self.assertEqual(result.name, "dfimagetools_recursive_hasher")
        self.assertIsNotNone(result.package)

        # Test with missing definitions
        _, test_file_path = tempfile.mkstemp(suffix=".yaml")

        try:
            with open(test_file_path, "w", encoding="utf-8") as file_object:
                file_object.write("---\n")

            runner = test_runner.TestRunner()
            with self.assertRaises(RuntimeError):
                runner.ReadTestConfiguration(test_file_path)

        finally:
            os.remove(test_file_path)

        # Test with multiple definitions
        yaml_content = "\n".join(
            [
                "---",
                "name: test1",
                "command: test1",
                "package:",
                "  path: /pkg1",
                "---",
                "name: test2",
                "command: test2",
                "package:",
                "  path: /pkg2",
                "",
            ]
        )
        _, test_file_path = tempfile.mkstemp(suffix=".yaml")

        try:
            with open(test_file_path, "w", encoding="utf-8") as file_object:
                file_object.write(yaml_content)

            runner = test_runner.TestRunner()
            with self.assertRaises(RuntimeError):
                runner.ReadTestConfiguration(test_file_path)

        finally:
            os.remove(test_file_path)

        # Test with empty file
        _, test_file_path = tempfile.mkstemp(suffix=".yaml")

        try:
            runner = test_runner.TestRunner()
            with open(test_file_path, "w", encoding="utf-8") as file_object:
                _ = file_object

            with self.assertRaises(RuntimeError):
                runner.ReadTestConfiguration(test_file_path)

        finally:
            os.remove(test_file_path)

    @mock.patch("clitooltester.test_runner.subprocess.run")
    def testRunTest(self, mock_subprocess_run):
        """Tests the RunTest function."""
        # Test with Docker configuration and subprocess.run success
        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        docker = resources.DockerDefinition()
        docker.tag = "test:latest"

        test_definition = resources.TestDefinition()
        test_definition.name = "test"
        test_definition.command = "ls"
        test_definition.docker = docker

        result = runner.RunTest(test_definition, silent=True)
        self.assertEqual(result, 0)

        # Test with Docker configuration, input and and subprocess.run success
        mock_subprocess_run.reset_mock()

        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        docker = resources.DockerDefinition()
        docker.tag = "test:latest"

        test_definition = resources.TestDefinition()
        test_definition.name = "test"
        test_definition.command = "ls %input%"
        test_definition.docker = docker

        test_input = resources.InputDefinition()
        test_input.name = "data"
        test_input.path = "/data/file.bin"

        result = runner.RunTest(test_definition, silent=True, test_input=test_input)
        self.assertEqual(result, 0)

        # Test with package configuration and subprocess.run success
        mock_subprocess_run.reset_mock()

        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        package = resources.PackageDefinition()
        package.path = "/home/user/pkg"

        test_definition = resources.TestDefinition()
        test_definition.name = "test"
        test_definition.command = "ls"
        test_definition.package = package

        result = runner.RunTest(test_definition, silent=True)
        self.assertEqual(result, 0)

        # Test with package configuration, input and subprocess.run success
        mock_subprocess_run.reset_mock()

        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        runner = test_runner.TestRunner()
        package = resources.PackageDefinition()
        package.path = "/home/user/pkg"

        test_definition = resources.TestDefinition()
        test_definition.name = "test"
        test_definition.command = "ls %input%"
        test_definition.package = package

        test_input = resources.InputDefinition()
        test_input.name = "data"
        test_input.path = "/data/file.bin"

        result = runner.RunTest(test_definition, silent=True, test_input=test_input)
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
