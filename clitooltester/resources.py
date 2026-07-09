"""Resources."""


class DockerDefinition:
    """Docker definition.

    Attributes:
      command (str): command to run inside the Docker container.
      dockerfile (str): path to a Dockerfile for building the image.
      tag (str): Docker image tag.
      volumes (list[DockerVolume]): volume mappings between host and container.
    """

    def __init__(self):
        """Initializes a Docker definition."""
        super().__init__()
        self.command = None
        self.dockerfile = None
        self.tag = None
        self.volumes = []


class DockerVolume:
    """Docker volume mapping.

    Attributes:
      docker_path (str): path inside the Docker container.
      host_path (str): path on the host machine.
    """

    def __init__(self):
        """Initializes a Docker volume."""
        super().__init__()
        self.docker_path = None
        self.host_path = None


class InputDefinition:
    """Input definition.

    Attributes:
      name (str): name that uniquely identifies the input.
      path (str): location of the input.
    """

    def __init__(self):
        """Initializes an input definition."""
        super().__init__()
        self.name = None
        self.path = None


class InputSetDefinition:
    """Input set definition.

    Attributes:
      base_path (str): base location of the input set, where the location (or path)
          of the elements are relative to the base location.
      elements (list[InputDefinition]): elements in the input set.
      name (str): name that uniquely identifies the input set.
    """

    def __init__(self):
        """Initializes an input set definition."""
        super().__init__()
        self.base_path = None
        self.elements = []
        self.name = None


class PackageDefinition:
    """Package definition.

    Attributes:
      build (str): command(s) to build the package.
      path (str): location of the package.
    """

    def __init__(self):
        """Initializes a package definition."""
        super().__init__()
        self.build = None
        self.path = None


class TestDefinition:
    """Test definition.

    Commands support placeholder arguments like %input%.

    Attributes:
      command (str): command with arguments.
      docker (DockerDefinition): Optional Docker configuration.
      name (str): name that uniquely identifies the test.
      package (PackageDefinition): package definition.
    """

    def __init__(self):
        """Initializes a test definition."""
        super().__init__()
        self.command = None
        self.docker = None
        self.name = None
        self.package = None
