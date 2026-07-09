"""YAML-based definitions files."""

import yaml

from clitooltester import resources


class YAMLInputsDefinitionsFile:
    """YAML-based inputs definitions file.

    A YAML-based inputs definitions file contains one or more input definitions. An
    input definition consists of:

    name: ext2
    path: test_data/ext2.raw

    Where:
    * name, that uniquely identifies the input;
    * path, location of the input.
    """

    _SUPPORTED_KEYS = frozenset(["name", "path"])

    def _ReadInputDefinition(self, yaml_input_definition):
        """Reads an input definition from a dictionary.

        Args:
          yaml_input_definition (dict[str, object]): YAML input definition values.

        Returns:
          InputDefinition: input definition.

        Raises:
          RuntimeError: if the format of the test definition is not set or incorrect.
        """
        if not yaml_input_definition:
            raise RuntimeError("Missing input definition values.")

        different_keys = set(yaml_input_definition) - self._SUPPORTED_KEYS
        if different_keys:
            different_keys = ", ".join(different_keys)
            raise RuntimeError(f"Undefined keys: {different_keys:s}")

        name = yaml_input_definition.get("name")
        if not name:
            raise RuntimeError("Invalid input definition missing name.")

        path = yaml_input_definition.get("path")
        if not path:
            raise RuntimeError("Invalid input definition missing path.")

        input_definition = resources.InputDefinition()
        input_definition.name = name
        input_definition.path = path

        return input_definition

    def _ReadFromFileObject(self, file_object):
        """Reads the input definions from a file-like object.

        Args:
          file_object (file): input definions file-like object.

        Yields:
          InputDefinition: input definition.
        """
        yaml_generator = yaml.safe_load_all(file_object)

        for yaml_input_definition in yaml_generator:
            yield self._ReadInputDefinition(yaml_input_definition)

    def ReadFromFile(self, path):
        """Reads the input definitions from a YAML file.

        Args:
          path (str): path to a input definitions file.

        Yields:
          InputDefinition: input definition.
        """
        with open(path, encoding="utf-8") as file_object:
            yield from self._ReadFromFileObject(file_object)


class YAMLTestDefinitionFile:
    """YAML-based test definitions file.

    A YAML-based test definitions file contains a test definition, which consists of:

    name: plaso_log2timeline
    command: log2timeline.py %input%
    package:
      path: /usr/bin

    Where:
    * name, that uniquely identifies the test;
    * command, with arguments, with can consist of placeholder values, such as: %input%.
    * docker, Docker configuration.
    * package, package configuration.
    """

    _SUPPORTED_KEYS = frozenset(["command", "docker", "name", "package"])

    def _ReadDockerDefinition(self, yaml_docker_definition):
        """Reads a Docker definition from a dictionary.

        Args:
          yaml_docker_definition (dict[str, object]): YAML Docker definition values.

        Returns:
          DockerDefinition: Docker definition.

        Raises:
          RuntimeError: if the format of the Docker definition is not set or incorrect.
        """
        if not yaml_docker_definition:
            raise RuntimeError("Missing Docker definition values.")

        tag = yaml_docker_definition.get("tag")
        if not tag:
            raise RuntimeError("Invalid Docker definition missing tag.")

        docker_definition = resources.DockerDefinition()
        docker_definition.tag = tag

        return docker_definition

    def _ReadPackageDefinition(self, yaml_package_definition):
        """Reads a package definition from a dictionary.

        Args:
          yaml_package_definition (dict[str, object]): YAML package definition values.

        Returns:
          PackageDefinition: package definition.

        Raises:
          RuntimeError: if the format of the package definition is not set or incorrect.
        """
        if not yaml_package_definition:
            raise RuntimeError("Missing package definition values.")

        path = yaml_package_definition.get("path")
        if not path:
            raise RuntimeError("Invalid package definition missing path.")

        package_definition = resources.PackageDefinition()
        package_definition.build = yaml_package_definition.get("build")
        package_definition.build_env = yaml_package_definition.get("build_env")
        package_definition.path = path

        return package_definition

    def _ReadTestDefinition(self, yaml_test_definition):
        """Reads a test definition from a dictionary.

        Args:
          yaml_test_definition (dict[str, object]): YAML test definition values.

        Returns:
          TestDefinition: test definition.

        Raises:
          RuntimeError: if the format of the test definition is not set or incorrect.
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

        docker_definition = yaml_test_definition.get("docker")
        package_definition = yaml_test_definition.get("package")
        if not docker_definition and not package_definition:
            raise RuntimeError("Invalid test definition missing docker and package.")

        test_definition = resources.TestDefinition()
        test_definition.command = command
        test_definition.name = name

        if docker_definition:
            test_definition.docker = self._ReadDockerDefinition(docker_definition)
        if package_definition:
            test_definition.package = self._ReadPackageDefinition(package_definition)

        return test_definition

    def _ReadFromFileObject(self, file_object):
        """Reads the test definition from a file-like object.

        Args:
          file_object (file): test definition file-like object.

        Yields:
          TestDefinition: test definition.
        """
        yaml_generator = yaml.safe_load_all(file_object)

        for yaml_test_definition in yaml_generator:
            yield self._ReadTestDefinition(yaml_test_definition)

    def ReadFromFile(self, path):
        """Reads the test definition from a YAML file.

        Args:
          path (str): path to a test definition file.

        Yields:
          TestDefinition: test definition.
        """
        with open(path, encoding="utf-8") as file_object:
            yield from self._ReadFromFileObject(file_object)
