from PyLOX.token import Token


class PyLOXParserError(Exception):
    def __init__(self, token: Token, message: str):
        super(PyLOXParserError, self).__init__("[line {line}, column {column}]: "
                                               "{message}".format(
            line=token.line,
            column=token.column,
            message=message))
        self.token = token


class PyLOXRuntimeError(Exception):
    def __init__(self, token: Token, description: str):
        super(PyLOXRuntimeError, self).__init__(
            "Runtime error at evaluation of {token} ({line}: {column}): "
            "{description}".format(token=token.type, line=token.line,
                                   column=token.column, description=description)
        )
        self.token = token
