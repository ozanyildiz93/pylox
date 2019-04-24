from PyLOX.exceptions import PyLOXRuntimeError
from PyLOX.token import Token


class Environment(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.memory = {}

    def define(self, name: Token, value: object) -> None:
        self.memory[name.lexeme] = value

    def __getitem__(self, name: Token):
        if name.lexeme in self.memory:
            return self.memory[name.lexeme]
        if self.parent is not None:
            return self.parent[name]
        raise PyLOXRuntimeError(name, "{name} is not defined in the current "
                                      "environment".format(name=name.lexeme))

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme not in self.memory:
            if self.parent is not None:
                self.parent.assign(name, value)
                return
            raise PyLOXRuntimeError(name, "{name} is not defined in the current"
                                          " environment".format(name=name.lexeme))
        self.memory[name.lexeme] = value
