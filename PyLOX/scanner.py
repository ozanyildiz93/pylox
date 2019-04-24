from typing import Any, List

from PyLOX.base_scanner import BaseScanner
from PyLOX.token import TokenType, Token

# characters
valid_characters = set("1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM*,;.+-_{}()*!=<>/" + '"')
digits = set("0123456789")
alpha = set("QWERTYUIOPASDFGHJKLZXCVBNM_qwertyuiopasdfghjklzxcvbnm")

# character to tokens
single_character_tokens = {
    "*": TokenType.STAR,
    ",": TokenType.COMMA,
    ";": TokenType.SEMICOLON,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    ".": TokenType.DOT,
    "(": TokenType.LEFT_PAREN,
    "{": TokenType.LEFT_BRACE,
    ")": TokenType.RIGHT_PAREN,
    "}": TokenType.RIGHT_BRACE
}

# maps to 3-tuple
# expected char, type if expected char is present, type otherwise
one_two_character_tokens = {
    "!": ("=", TokenType.BANG_EQUAL, TokenType.BANG),
    "=": ("=", TokenType.EQUAL_EQUAL, TokenType.EQUAL),
    "<": ("=", TokenType.LESS_EQUAL, TokenType.LESS),
    ">": ("=", TokenType.GREATER_EQUAL, TokenType.GREATER)
}

keywords = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUNC,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
    "break": TokenType.BREAK
}


class Scanner(BaseScanner):
    def __init__(self, source):
        super(Scanner, self).__init__(source)
        self.line = 0
        self.column = 0
        self.valid = True

    def scan_tokens(self) -> List[Token]:
        tokens = []

        while not self.is_finished():
            token = self.scan_token()
            tokens.append(token)

        tokens.append(Token(TokenType.EOF, "", None, self.line, self.column))
        return tokens

    def tokenize(self, type: TokenType, literal: Any = None) -> Token:
        # creates a token using recorded part of the source
        lexeme = self.stop_recording()
        return Token(type, lexeme, literal, self.line, self.column)

    def register_newline(self) -> None:
        # register a newline
        self.line += 1
        self.column = 0

    def advance(self):
        # overwrite advance to increment column
        self.column += 1
        super(Scanner, self).advance()

    def is_current_char_whitespace(self) -> bool:
        # returns true if current character corresponds to a whitespace
        return self.peek() in set(" \t")

    def is_current_char_newline(self) -> bool:
        # returns true if current character is a newline
        return self.peek() in set("\r\n")

    def consume_newline(self) -> None:
        self.match("\r\n")
        while self.is_current_char_newline():
            self.consume()
        self.register_newline()

    def consume_whitespace(self) -> None:
        while True:
            if self.is_current_char_whitespace():
                self.consume()
            elif self.is_current_char_newline():
                self.consume_newline()
            else:
                return

    def consume_until_newline(self) -> None:
        # helper function for comment
        while not self.is_finished() and not self.is_current_char_newline():
            self.consume()
        self.consume_newline()

    def scan_token(self) -> Token:
        # skip whitespaces
        self.consume_whitespace()
        self.start_recording()
        character = self.consume()

        # check for end of source file
        if character is None:
            token = self.tokenize(TokenType.EOF)
            return token

        # check for unrecognized characters
        if character not in valid_characters:
            self.valid = False
            self.error("Unexpected character {char}".format(char=character))
            token = self.tokenize(TokenType.INVALID)
            return token

        # check for tokens of size 1
        if character in single_character_tokens:
            token = self.tokenize(single_character_tokens[character])
            return token

        # check for variable sized tokens with size 1 or 2
        if character in one_two_character_tokens:
            expected_char = one_two_character_tokens[character][0]
            if self.match([expected_char]):
                token_type = one_two_character_tokens[character][1]
            else:
                token_type = one_two_character_tokens[character][2]
            token = self.tokenize(token_type)
            return token

        # check for divide/comment
        if character == "/":
            if self.match("/"):
                self.consume_until_newline()
                token_type = TokenType.COMMENT
            elif self.match("*"):
                depth = 1
                character = self.peek()
                while depth > 0:
                    if self.is_current_char_newline():
                        self.consume_newline()
                        character = self.consume()
                    next_character = self.consume()
                    if character == "*":
                        if next_character == "/":
                            depth -= 1
                    elif character == "/":
                        if next_character == "*":
                            depth += 1
                    character = next_character
                token_type = TokenType.MULTILINE_COMMENT
            else:
                token_type = TokenType.SLASH
            token = self.tokenize(token_type)
            return token

        # check for string
        if character == '"':
            while not self.is_finished():
                if self.is_current_char_newline():
                    self.consume_newline()
                if self.consume() == '"':
                    # remove enclosing "s
                    value = self.stop_recording(reset=False)[1:-1]
                    token = self.tokenize(TokenType.STRING, value)
                    break
            else:
                # source is finished
                self.error("Unterminated string.")
                token = self.tokenize(TokenType.INVALID)
            return token

        # check for number literal
        if character in digits:
            while not self.is_finished():
                character = self.peek()
                if character in digits:
                    self.consume()
                elif character == "." and self.peek(1) in digits:
                    self.consume()
                else:
                    break

            value = float(self.stop_recording(reset=False))
            token = self.tokenize(TokenType.NUMBER, value)
            return token

        if character in alpha:
            value = character
            while not self.is_finished():
                if self.peek() in alpha:
                    value += self.consume()
                elif self.peek() in digits:
                    value += self.consume()
                else:
                    break
            if value in keywords:
                token = self.tokenize(keywords[value])
            else:
                token = self.tokenize(TokenType.IDENTIFIER, value)
            return token

        raise NotImplementedError("{char} does not match to start of any known token".format(char=character))

    def error(self, message: str) -> None:
        self.report("", message)

    def report(self, where: str, message: str) -> None:
        print("[line {line}, column {column}] {where}: {message}".format(
            line=self.line,
            column=self.column,
            where=where,
            message=message))
