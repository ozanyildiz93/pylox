from typing import List

from PyLOX.expressions import Expr
from PyLOX.token import Token


class Stmt(object):
    def visit(self, visitor, *args, **kwargs):
        pass


class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_expression(self, *args, **kwargs)


class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_print(self, *args, **kwargs)


class Var(Stmt):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_var(self, *args, **kwargs)


class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_block(self, *args, **kwargs)


class If(Stmt):
    def __init__(self, condition: Expr, then_statement: Stmt, else_statement: Stmt):
        self.condition = condition
        self.then_statement = then_statement
        self.else_statement = else_statement

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_if(self, *args, **kwargs)


class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_while(self, *args, **kwargs)


class Break(Stmt):
    def __init__(self, token: Token):
        self.token = token

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_break(self, *args, **kwargs)
