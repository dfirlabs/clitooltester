"""Resources."""


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
      name (str): name that uniquely identifies the test.
    """

    def __init__(self):
        """Initializes a test definition."""
        super().__init__()
        self.command = None
        self.name = None
