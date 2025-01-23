class PlayerCommand(Command):
    def __init__(self, name, description, required_role=None):
        super().__init__(name, description, required_role)

    def execute(self, player, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")