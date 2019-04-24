from enum import Enum, auto


class TokenType(Enum):
    # Single-character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()

    # One or two charavter tokens
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FUNC = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()
    BREAK = auto()

    # internal use only
    MULTILINE_COMMENT = auto()
    COMMENT = auto()
    INVALID = auto()
    EOF = auto()

    def __str__(self):
        return self.name


class Token(object):
    def __init__(self, type: TokenType, lexeme: str, literal: object,
                 line: int, column: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.column = column

    def __str__(self):
        return "Token({type} {lexeme} {literal})".format(type=self.type,
                                                         lexeme=self.lexeme,
                                                         literal=self.literal)

    def __eq__(self, rhs: object) -> bool:
        if isinstance(rhs, Token):
            return self.type == rhs.type and self.literal == rhs.literal
        elif isinstance(rhs, TokenType):
            return self.type == rhs
        raise ValueError("Expecting an instance of Token or TokeType, "
                         "instead received instance of{type}".format(
            type=type(rhs)))

    def __hash__(self):
        return hash(self.type)
