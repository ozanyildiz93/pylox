from typing import Any, List

from PyLOX.token import TokenType, Token


class Scanner(object):
    def __init__(self, source):
        self.source = source
        self.start = 0
        self.line = 0
        self.column = 0

    def scan_tokens(self) -> List[Token]:
        tokens = []

        while not self.is_finished():
            token = self.scan_token()
            tokens.append(token)

        tokens.append(Token(TokenType.EOF, "", None, self.line, self.column))
        return tokens

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
        "while": TokenType.WHILE
    }

    valid_characters = set("1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM*,;.+-_{}()*!=<>/" + '"')
    digits = set("0123456789")
    alpha = set("QWERTYUIOPASDFGHJKLZXCVBNM_qwertyuiopasdfghjklzxcvbnm")

    def tokenize(self, start: int, type: TokenType, literal: Any = None) -> Token:
        # creates a token starting from start and ends at self.start
        lexeme = self.source[start: self.start]
        return Token(type, lexeme, literal, self.line, self.column)

    def match(self, expected: chr) -> bool:
        # consumes the next character if matches to expected and returns True
        if self.is_finished():
            return False
        current = self.get_current_character()
        if current == expected:
            self.advance()
            return True
        return False

    def advance(self) -> None:
        # increments start and column
        self.start += 1
        self.column += 1

    def get_current_character(self) -> chr:
        # returns the current character
        if self.start < len(self.source):
            return self.source[self.start]
        else:
            return ""

    def get_next_character(self) -> chr:
        # returns the next character
        if self.start + 1 < len(self.source):
            return self.source[self.start + 1]
        return ""

    def consume(self) -> chr:
        # returns current character and advances scanner by one character
        # if at the end of source, returns None
        result = self.get_current_character()
        self.advance()
        return result

    def is_finished(self) -> bool:
        # returns true if current index passed the end of source
        return self.start >= len(self.source)

    def register_newline(self) -> None:
        # register a newline
        self.line += 1
        self.column = 0

    def is_current_char_whitespace(self) -> bool:
        # returns true if current character corresponds to a whitespace
        return self.get_current_character() in set(" \t")

    def is_current_char_newline(self) -> bool:
        # returns true if current character is a newline
        return self.get_current_character() in set("\r\n")

    def consume_newline(self) -> None:
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
        start = self.start
        character = self.consume()

        # check for end of source file
        if character is "":
            token = self.tokenize(start, TokenType.EOF)
            return token

        # check for unrecognized characters
        if character not in Scanner.valid_characters:
            self.error("Unexpected character {char}".format(char=character))
            token = self.tokenize(start, TokenType.INVALID)
            return token

        # check for tokens of size 1
        if character in Scanner.single_character_tokens:
            token = self.tokenize(start, Scanner.single_character_tokens[character])
            return token

        # check for variable sized tokens with size 1 or 2
        if character in Scanner.one_two_character_tokens:
            expected_char = Scanner.one_two_character_tokens[character][0]
            if self.match(expected_char):
                token_type = Scanner.one_two_character_tokens[character][1]
            else:
                token_type = Scanner.one_two_character_tokens[character][2]
            token = self.tokenize(start, token_type)
            return token

        # check for divide/comment
        if character == "/":
            if self.match("/"):
                start += 2
                self.consume_until_newline()
                token_type = TokenType.COMMENT
            elif self.match("*"):
                depth = 1
                character = self.get_current_character()
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
            token = self.tokenize(start, token_type)
            return token

        # check for string
        if character == '"':
            while not self.is_finished():
                if self.is_current_char_newline():
                    self.consume_newline()
                if self.consume() == '"':
                    # remove enclosing "s
                    value = self.source[start + 1:self.start - 1]
                    token = self.tokenize(start, TokenType.STRING, value)
                    break
            else:
                # source is finished
                self.error("Unterminated string.")
                token = self.tokenize(start, TokenType.INVALID)
            return token

        # check for number literal
        if character in Scanner.digits:
            while not self.is_finished():
                character = self.get_current_character()
                if character in Scanner.digits:
                    self.consume()
                elif character == "." and self.get_next_character() in Scanner.digits:
                    self.consume()
                else:
                    break

            value = float(self.source[start:self.start])
            token = self.tokenize(start, TokenType.NUMBER, value)
            return token

        if character in Scanner.alpha:
            value = character
            while not self.is_finished():
                if self.get_current_character() in Scanner.alpha:
                    value += self.consume()
                elif self.get_current_character() in Scanner.digits:
                    value += self.consume()
                else:
                    break
            if value in Scanner.keywords:
                token = self.tokenize(start, Scanner.keywords[value])
            else:
                token = self.tokenize(start, TokenType.IDENTIFIER, value)
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
