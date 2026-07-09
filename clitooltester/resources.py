"""Resources."""


class DockerDefinition:
    """Docker definition.

    Attributes:
      command (str): command to run inside the Docker container.
      tag (str): Docker image tag.
      volumes (list[DockerVolume]): volume mappings between host and container.
    """

    def __init__(self):
        """Initializes a Docker definition."""
        super().__init__()
        self.command = None
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


class TestDefinition:
    """Test definition.

    Attributes:
      command (str): command with arguments, with can consist of placeholder values,
          such as: %input%.
      docker (DockerDefinition): Optional Docker configuration.
      name (str): name that uniquely identifies the test.
    """

    def __init__(self):
        """Initializes a test definition."""
        super().__init__()
        self.command = None
        self.docker = None
        self.name = None
