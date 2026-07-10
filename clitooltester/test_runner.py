"""Command line tool test runner."""

import os
import pathlib
import subprocess

from clitooltester import yaml_definitions_file


class TestRunner:
    """Command line tool test runner."""

    def __init__(self, quiet=False, verbose=False):
        """Initializes a command line tool test runner.

        Args:
          quiet (Optional[bool]): value to indicate all prints should be disabled,
              overrides verbose.
          verbose (Optional[bool]): value to indicate stdout and stderr should be
              printed on error.
        """
        super().__init__()
        self._quiet = quiet
        self._verbose = verbose

    def _RunTestWithDocker(self, test_definition, test_input=None):
        """Runs a test with Docker.

        Args:
          test_definition (TestDefinition): test definition with Docker configuration.
          test_input (Optional[InputDefinition]): input definition.

        Returns:
          int: exit code from the test command.

        Raises:
          ValueError: if the Docker configuration is missing.
        """
        if not test_definition.docker:
            raise ValueError("Invalid test definition - missing Docker configuration")

        test_values = {}

        test_description = f"{test_definition.name:s}"
        arguments = ["docker", "run", "--rm"]

        if test_input:
            path = pathlib.Path(test_input.path)

            arguments.extend(["-v", f"{path.parent!s}:/input:z"])
            test_description = f"{test_description:s} with input: '{test_input.name:s}'"
            test_values["%input%"] = f'"/input/{path.name:s}"'

        docker_definition = test_definition.docker

        command = self._SubstitutePlaceholders(test_definition.command, test_values)
        arguments.extend([docker_definition.tag, command])

        if not self._quiet:
            print(test_description, end="")

        result = subprocess.run(
            arguments,
            capture_output=True,
            check=False,
            shell=True,
            text=True,
        )
        if not self._quiet:
            padding_length = max(1, 72 - len(test_description))
            print(" " * padding_length, end="")

            if result.returncode == 0:
                print("\033[32mok\033[0m")
            else:
                print("\033[31mFAILED\033[0m")

                if self._verbose and result.stdout:
                    print(result.stdout)
                if self._verbose and result.stderr:
                    print(result.stderr)

        return result.returncode

    def _RunTestWithPackage(self, test_definition, test_input=None):
        """Runs a test.

        Args:
          test_definition (TestDefinition): test definition with Docker configuration.
          test_input (Optional[InputDefinition]): input definition.

        Returns:
          int: exit code from the test command.

        Raises:
          ValueError: if the package configuration is missing.
        """
        if not test_definition.package:
            raise ValueError("Invalid test definition - missing package configuration")

        test_description = f"{test_definition.name:s}"
        test_values = {"%package%": f'"{test_definition.package.path:s}"'}

        if test_input:
            test_description = f"{test_description:s} with input: '{test_input.name:s}'"
            test_values["%input%"] = f'"{test_input.path:s}"'

        command = self._SubstitutePlaceholders(test_definition.command, test_values)
        arguments = [command]

        if not self._quiet:
            print(test_description, end="")

        result = subprocess.run(
            arguments,
            capture_output=True,
            check=False,
            shell=True,
            text=True,
        )
        if not self._quiet:
            padding_length = max(1, 72 - len(test_description))
            print(" " * padding_length, end="")

            if result.returncode == 0:
                print("\033[32mok\033[0m")
            else:
                print("\033[31mFAILED\033[0m")

                if self._verbose and result.stdout:
                    print(result.stdout)
                if self._verbose and result.stderr:
                    print(result.stderr)

        return result.returncode

    def _SubstitutePlaceholders(self, command, test_values):
        """Substitutes placeholders in a command.

        Supported placeholders:
          "%input%", which represents the path of the input.
          "%package%", which represents the path of the package.

        Args:
          command (str): command with placeholders.
          test_values (dict[str, str]): test values per placeholder.

        Returns:
          str: command with placeholders substituted.
        """
        for key, value in test_values.items():
            command = command.replace(key, value)

        return command

    def BuildPackage(self, test_definition):
        """Builds a package before running tests.

        Args:
          test_definition (TestDefinition): test definition with Docker configuration.

        Returns:
          int: exit code from the test command.

        Raises:
          ValueError: if the package configuration is missing.
        """
        if not test_definition.package:
            raise ValueError("Invalid test definition - missing package configuration")

        test_values = {"%package%": f'"{test_definition.package.path:s}"'}

        # Note that the user shell is used to not to have to set up the build
        # environment.
        shell = os.environ.get("SHELL", "/bin/bash")

        command = self._SubstitutePlaceholders(
            test_definition.package.build, test_values
        )
        arguments = [shell, "-l", "-i", "-c", command]

        result = subprocess.run(
            arguments,
            capture_output=True,
            check=False,
            cwd=test_definition.package.path,
            env=test_definition.package.build_env,
            shell=False,
            text=True,
        )
        if not self._quiet and result.returncode != 0:
            if self._verbose and result.stdout:
                print(result.stdout)
            if self._verbose and result.stderr:
                print(result.stderr)

        return result.returncode

    def BuildDockerImage(self, test_definition):
        """Builds a Docker image from a Dockerfile.

        Args:
          test_definition (TestDefinition): test definition with Docker configuration.

        Returns:
          int: exit code from the test command.

        Raises:
          ValueError: if the Docker configuration is missing.
        """
        if not test_definition.docker:
            raise ValueError("Invalid test definition - missing Docker configuration")

        if not test_definition.docker.dockerfile:
            raise ValueError("Invalid Docker definition - missing dockerfile")

        arguments = [
            "docker",
            "build",
            "-t",
            test_definition.docker.tag,
            "-f",
            test_definition.docker.dockerfile,
            ".",
        ]
        result = subprocess.run(
            arguments,
            capture_output=True,
            check=False,
            shell=False,
            text=True,
        )
        if not self._quiet and result.returncode != 0:
            if self._verbose and result.stdout:
                print(result.stdout)
            if self._verbose and result.stderr:
                print(result.stderr)

        return result.returncode

    def ReadInputsConfiguration(self, path):
        """Reads the inputs configuration from a file.

        Args:
          path (str): path of the configuration file.

        Returns:
          list[InputDefinitions]: input definitions.
        """
        yaml_definition_file = yaml_definitions_file.YAMLInputsDefinitionsFile()

        return list(yaml_definition_file.ReadFromFile(path))

    def ReadTestConfiguration(self, path):
        """Reads the test configuration from a file.

        Args:
          path (str): path of the configuration file.

        Returns:
          TestDefinition: test definition.

        Raises:
          RuntimeError: if test definition is missing.
        """
        yaml_definition_file = yaml_definitions_file.YAMLTestDefinitionFile()

        test_definitions = list(yaml_definition_file.ReadFromFile(path))
        if not test_definitions:
            raise RuntimeError("Missing test definitions")

        if len(test_definitions) != 1:
            raise RuntimeError("More than 1 test definition currently not supported")

        return test_definitions[0]

    def RunTest(self, test_definition, test_input=None):
        """Runs a test.

        Args:
          test_definition (TestDefinition): test definition with Docker configuration.
          test_input (Optional[InputDefinition]): input definition.

        Returns:
          int: exit code from the test command.

        Raises:
          ValueError: if the package configuration is missing.
        """
        if test_definition.docker:
            return self._RunTestWithDocker(test_definition, test_input=test_input)

        return self._RunTestWithPackage(test_definition, test_input=test_input)
