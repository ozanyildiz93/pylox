from typing import Callable, List

from PyLOX.base_scanner import BaseScanner
from PyLOX.exceptions import PyLOXParserError
from PyLOX.expressions import Expr, Binary, Grouping, Literal, Unary, \
    Variable, Assignment, Logical
from PyLOX.statements import Stmt, Print, Var, Expression, Block, If, While, \
    Break
from PyLOX.token import TokenType

"""
Parsing rules:
    program             : declaration* EOF
    declaration         : variableDeclaration | statement
    
    variableDeclaration : "var" IDENTIFIER ( "=" expression )? ";"
    
    statement           : expressionStatement | printStatement | block 
                                | ifStatement | whileStatement | forStatement
                                | breakStatement
    expressionStatement : expression ";"
    printStatement      : "print" expression ";"
    block               : "{" declaration* "}"
    ifStatement         : "if" "(" expression ")" statement ( "else" statement )?
    whileStatement      : "while" "(" expression ")" statement
    forStatement        : "for" "(" ( variableDeclaration | expressionStatement | ";" )
                                    expression ? ";" expression ? ")" statement
    breakStatement      : "break" ";"
    
    expression          : assignment
    assignment          : IDENTIFIER "=" assignment | logical_or
    logical_or          : logical_and ( "or" logical_and )*
    logical_and         : equality ( "and" equality )*
    equality            : comparison ( ( "!=" | "==" ) comparison )*
    comparison          : addition ( ( ">" | ">=" | "<" | "<=" ) addition )*
    addition            : multiplication ( ( "+" | "-" ) multiplication )*
    multiplication      : unary ( ( "*" | "/" ) ) unary )*
    unary               : ( "!" | "-" ) unary | primary
    primary             : NUMBER | STRING | IDENTIFIER | "false" | "true" 
                                | "nil"  | "(" expression ")"
"""


class Parser(BaseScanner):
    def __init__(self, *args, **kwargs):
        super(Parser, self).__init__(*args, **kwargs)
        self.valid = True

    def parse(self) -> List[Stmt]:
        return self.program()

    def program(self) -> List[Stmt]:
        declarations = []
        while not self.match([TokenType.EOF]):
            try:
                declarations.append(self.declaration())
            except PyLOXParserError as e:
                self.valid = False
                print(e)
                self.synchronize()
        return declarations

    def declaration(self) -> Stmt:
        if self.match([TokenType.VAR]):
            return self.variable_declaration()
        return self.statement()

    def variable_declaration(self) -> Stmt:
        # var is already consumed
        identifier = self.consume(TokenType.IDENTIFIER, "IDENTIFIER")
        if self.match([TokenType.EQUAL]):
            value = self.expression()
        else:
            value = None
        self.consume(TokenType.SEMICOLON, ";")
        return Var(identifier, value)

    def statement(self) -> Stmt:
        branches = {
            TokenType.PRINT: self.print_statement,
            TokenType.LEFT_BRACE: self.block,
            TokenType.IF: self.if_statement,
            TokenType.WHILE: self.while_statement,
            TokenType.FOR: self.for_statement,
            TokenType.BREAK: self.break_statement,
        }
        return branches.get(self.peek(), self.expression_statement)()

    def print_statement(self) -> Stmt:
        self.consume(TokenType.PRINT, "print")
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, ";")
        return Print(expr)

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, ";")
        return Expression(expr)

    def block(self) -> Stmt:
        self.consume(TokenType.LEFT_BRACE, "{")
        declarations = []
        while self.peek() != TokenType.RIGHT_BRACE and not self.is_finished():
            declaration = self.declaration()
            declarations.append(declaration)
        self.consume(TokenType.RIGHT_BRACE, "}")
        return Block(declarations)

    def if_statement(self) -> Stmt:
        self.consume(TokenType.IF, "if")
        self.consume(TokenType.LEFT_PAREN, "(")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, ")")
        then_statement = self.statement()
        if self.match([TokenType.ELSE]):
            else_statement = self.statement()
        else:
            else_statement = None
        return If(condition, then_statement, else_statement)

    def while_statement(self) -> Stmt:
        self.consume(TokenType.WHILE, "while")
        self.consume(TokenType.LEFT_PAREN, "(")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, ")")
        statement = self.statement()
        return While(condition, statement)

    def for_statement(self) -> Stmt:
        self.consume(TokenType.FOR, "for")
        self.consume(TokenType.LEFT_PAREN, "(")
        if self.match([TokenType.SEMICOLON]):
            initializer = None
        elif self.match([TokenType.VAR]):
            initializer = self.variable_declaration()
        else:
            initializer = self.expression_statement()
        if self.match([TokenType.SEMICOLON]):
            condition = Literal(True)
        else:
            condition = self.expression()
            self.consume(TokenType.SEMICOLON, ";")
        if self.match([TokenType.RIGHT_PAREN]):
            update = None
        else:
            update = self.expression()
            self.consume(TokenType.RIGHT_PAREN, ")")

        body = self.statement()
        if update is not None:
            body = Block([body, Expression(update)])
        body = While(condition, body)
        if initializer is not None:
            body = Block([initializer, body])
        return body

    def break_statement(self) -> Stmt:
        token = self.peek()
        self.consume(TokenType.BREAK, "break")
        self.consume(TokenType.SEMICOLON, ";")
        return Break(token)

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expr = self.logical_or()
        if self.match([TokenType.EQUAL]):
            if not isinstance(expr, Variable):
                print(PyLOXParserError(self.peek(-1), "Invalid assignment target"))
                self.valid = False
                return self.assignment()

            assignee = self.assignment()
            return Assignment(expr.name, assignee)
        return expr

    def logical_or(self) -> Expr:
        left = self.logical_and()
        while self.match([TokenType.OR]):
            operator = self.peek(-1)
            right = self.logical_and()
            left = Logical(left, operator, right)
        return left

    def logical_and(self) -> Expr:
        left = self.equality()
        while self.match([TokenType.AND]):
            operator = self.peek(-1)
            right = self.equality()
            left = Logical(left, operator, right)
        return left

    def binary_expression(self, types: List[TokenType],
                          child_parser: Callable) -> Expr:
        left = child_parser()
        while self.match(types):
            operator = self.peek(-1)
            right = child_parser()
            left = Binary(left, operator, right)
        return left

    def equality(self) -> Expr:
        return self.binary_expression([TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL],
                                      self.comparison)

    def comparison(self) -> Expr:
        return self.binary_expression([TokenType.LESS, TokenType.LESS_EQUAL,
                                       TokenType.GREATER, TokenType.GREATER_EQUAL],
                                      self.addition)

    def addition(self) -> Expr:
        return self.binary_expression([TokenType.PLUS, TokenType.MINUS],
                                      self.multiplication)

    def multiplication(self) -> Expr:
        return self.binary_expression([TokenType.STAR, TokenType.SLASH],
                                      self.unary)

    def unary(self) -> Expr:
        if self.match([TokenType.BANG, TokenType.MINUS]):
            operator = self.peek(-1)
            right = self.unary()
            return Unary(operator, right)
        return self.primary()

    def primary(self) -> Expr:
        if self.match([TokenType.FALSE]):
            return Literal(False)
        if self.match([TokenType.TRUE]):
            return Literal(True)
        if self.match([TokenType.NIL]):
            return Literal(None)
        if self.match([TokenType.STRING, TokenType.NUMBER]):
            token = self.peek(-1)
            return Literal(token.literal)
        if self.match([TokenType.IDENTIFIER]):
            token = self.peek(-1)
            return Variable(token)
        if self.match([TokenType.LEFT_PAREN]):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, ")")
            return Grouping(expr)

        # I am not sure what I was expecting
        raise PyLOXParserError(self.peek(), "Parser was expecting a literal "
                                            "instead found {token}".format(
            token=self.peek()))

    def synchronize(self) -> None:
        # search for end/start of a statement
        while not self.match([TokenType.SEMICOLON]):
            if self.match([TokenType.CLASS,
                           TokenType.FUNC,
                           TokenType.FOR,
                           TokenType.VAR,
                           TokenType.IF,
                           TokenType.WHILE,
                           TokenType.PRINT,
                           TokenType.RETURN]):
                # we need keyword for next statement
                self.rewind()
                return
            elif self.peek() == TokenType.EOF:
                return
            else:
                self.advance()

    def advance(self):
        super(Parser, self).advance()
        while self.peek() == TokenType.COMMENT:
            super(Parser, self).advance()

    def consume(self, target: TokenType, expected: str):
        if self.peek() == target:
            return super(Parser, self).consume()
        raise PyLOXParserError(self.peek(), 'Parser was expecting "{expected}"'
                                            ' instead found "{found}"'.format(
            expected=expected,
            found=self.peek()
        ))
