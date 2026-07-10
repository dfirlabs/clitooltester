"""Command line tool test runner."""

import os
import pathlib
import re
import shlex
import shutil
import subprocess

from concurrent import futures

from clitooltester import resources
from clitooltester import yaml_definitions_file


class TestRunner:
    """Command line tool test runner."""

    _PLACEHOLDER_RE = re.compile(r"%[0-9A-Za-z_]+%")

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

    def _PrintTestResult(self, test_result):
        """Prints a test result.

        Args:
          test_result (TestResult): test result.
        """
        if self._quiet:
            return

        print(test_result.description, end="")

        padding_length = max(1, 72 - len(test_result.description))
        print(" " * padding_length, end="")

        if test_result.exit_code == 0:
            print("\033[32mok\033[0m")
        else:
            print("\033[31mFAILED\033[0m")

            if self._verbose and test_result.stdout:
                print(test_result.stdout)
            if self._verbose and test_result.stderr:
                print(test_result.stderr)

    def _RunTestWithDocker(self, test_definition, test_input=None):
        """Runs a test with Docker.

        Args:
          test_definition (TestDefinition): test definition with Docker configuration.
          test_input (Optional[InputDefinition]): input definition.

        Returns:
          TestResult: test result.

        Raises:
          RuntimeError: if unable to find docker binary or if the command contains
              unresolved placeholders.
          ValueError: if the Docker configuration is missing.
        """
        if not test_definition.docker:
            raise ValueError("Invalid test definition - missing Docker configuration")

        docker_path = shutil.which("docker")
        if not docker_path:
            raise RuntimeError("Unable to determine location of docker binary")

        arguments = [docker_path, "run", "--rm"]
        test_description = f"{test_definition.name:s}"
        test_parameters = {}

        if test_input:
            path = pathlib.Path(test_input.path)
            if not path.is_absolute():
                path = path.resolve()

            arguments.extend(["-v", f"{path.parent!s}:/input:z"])
            test_description = f"{test_description:s} with input: '{test_input.name:s}'"
            test_parameters = {
                f"%{key:s}%": str(value) for key, value in test_input.parameters.items()
            }
            test_parameters["%input%"] = f'"/input/{path.name:s}"'

        docker_definition = test_definition.docker

        arguments.append(docker_definition.tag)

        command = self._SubstitutePlaceholders(test_definition.command, test_parameters)

        matches = self._PLACEHOLDER_RE.findall(command)
        if matches:
            placeholders = ", ".join(matches)
            raise RuntimeError(
                f"Command contains unresolved placeholders: {placeholders:s}"
            )

        arguments.extend(shlex.split(command))

        subprocess_result = subprocess.run(
            arguments,
            capture_output=True,
            check=False,
            shell=False,
            text=True,
        )
        test_result = resources.TestResult()
        test_result.description = test_description
        test_result.exit_code = subprocess_result.returncode
        test_result.stderr = subprocess_result.stderr
        test_result.stdout = subprocess_result.stdout

        return test_result

    def _RunTestWithPackage(self, test_definition, test_input=None):
        """Runs a test.

        Args:
          test_definition (TestDefinition): test definition with Docker configuration.
          test_input (Optional[InputDefinition]): input definition.

        Returns:
          TestResult: test result.

        Raises:
          RuntimeError: if the command contains unresolved placeholders.
          ValueError: if the package configuration is missing.
        """
        if not test_definition.package:
            raise ValueError("Invalid test definition - missing package configuration")

        test_description = f"{test_definition.name:s}"
        test_parameters = {}

        if test_input:
            test_description = f"{test_description:s} with input: '{test_input.name:s}'"
            test_parameters = {
                f"%{key:s}%": str(value) for key, value in test_input.parameters.items()
            }
            test_parameters["%input%"] = f'"{test_input.path:s}"'

        command = self._SubstitutePlaceholders(test_definition.command, test_parameters)

        matches = self._PLACEHOLDER_RE.findall(command)
        if matches:
            placeholders = ", ".join(matches)
            raise RuntimeError(
                f"Command contains unresolved placeholders: {placeholders:s}"
            )

        arguments = shlex.split(command)

        subprocess_result = subprocess.run(
            arguments,
            capture_output=True,
            check=False,
            shell=True,
            text=True,
        )
        test_result = resources.TestResult()
        test_result.description = test_description
        test_result.exit_code = subprocess_result.returncode
        test_result.stderr = subprocess_result.stderr
        test_result.stdout = subprocess_result.stdout

        return test_result

    def _SubstitutePlaceholders(self, command, test_parameters):
        """Substitutes placeholders in a command.

        Supported placeholders:
          "%input%", which represents the path of the input.
          "%package%", which represents the path of the package.

        Args:
          command (str): command with placeholders.
          test_parameters (dict[str, str]): test parameters.

        Returns:
          str: command with placeholders substituted.
        """
        for key, value in test_parameters.items():
            command = command.replace(key, value)

        return command

    def BuildPackage(self, test_definition):
        """Builds a package before running tests.

        Args:
          test_definition (TestDefinition): test definition with Docker configuration.

        Returns:
          int: exit code from the build command.

        Raises:
          RuntimeError: if the command contains unresolved placeholders.
          ValueError: if the package configuration is missing.
        """
        if not test_definition.package:
            raise ValueError("Invalid test definition - missing package configuration")

        # Note that the user shell is used to not to have to set up the build
        # environment.
        shell = os.environ.get("SHELL", "/bin/bash")

        arguments = [shell, "-l", "-i", "-c"]
        test_parameters = {"%package%": f'"{test_definition.package.path:s}"'}

        command = self._SubstitutePlaceholders(
            test_definition.package.build, test_parameters
        )
        matches = self._PLACEHOLDER_RE.findall(command)
        if matches:
            placeholders = ", ".join(matches)
            raise RuntimeError(
                f"Command contains unresolved placeholders: {placeholders:s}"
            )

        arguments.extend(shlex.split(command))

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
          int: exit code from the build command.

        Raises:
          RuntimeError: if unable to find docker binary.
          ValueError: if the Docker configuration is missing.
        """
        if not test_definition.docker:
            raise ValueError("Invalid test definition - missing Docker configuration")

        if not test_definition.docker.dockerfile:
            raise ValueError("Invalid Docker definition - missing dockerfile")

        docker_path = shutil.which("docker")
        if not docker_path:
            raise RuntimeError("Unable to determine location of docker binary")

        arguments = [
            docker_path,
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
          TestResult: test result.

        Raises:
          ValueError: if the package configuration is missing.
        """
        if test_definition.docker:
            return self._RunTestWithDocker(test_definition, test_input=test_input)

        return self._RunTestWithPackage(test_definition, test_input=test_input)

    def RunTests(self, test_definition, jobs=1, test_inputs=None):
        """Runs tests and collects results.

        Args:
          test_definition (TestDefinition): test definition.
          jobs (Optional[int]): number of parallel jobs to run, where 1 is sequential.
          test_inputs (Optional[list[InputDefinition]]): input definitions.

        Returns:
          list[int]: list of exit codes from each test.
        """
        if test_inputs:
            tasks = [(test_definition, test_input) for test_input in test_inputs]
        else:
            tasks = [(test_definition, None)]

        if jobs <= 1:
            results = []
            for task in tasks:
                test_runner = TestRunner(quiet=self._quiet, verbose=self._verbose)
                test_result = test_runner.RunTest(*task)

                results.append(test_result)

                self._PrintTestResult(test_result)

            return results

        results = [None] * len(tasks)

        def _run_job(index, task):
            test_runner = TestRunner(quiet=self._quiet, verbose=self._verbose)
            return index, test_runner.RunTest(*task)

        with futures.ThreadPoolExecutor(max_workers=jobs) as executor:
            future_instances = {
                executor.submit(_run_job, index, task): (index, task)
                for index, task in enumerate(tasks)
            }
            for future in futures.as_completed(future_instances):
                index, test_result = future.result()
                results[index] = test_result

                self._PrintTestResult(test_result)

        return results
