from abc import ABC, abstractmethod

class Command:
    def __init__(self, name, description, required_roles=None):
        self.name = name
        self.description = description
        self.required_roles = required_roles or []

    @abstractmethod
    def execute(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")