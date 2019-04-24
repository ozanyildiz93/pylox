from functools import partial, wraps
from typing import List

from PyLOX.environment import Environment
from PyLOX.exceptions import PyLOXRuntimeError
from PyLOX.expressions import Binary, Grouping, Literal, Unary, \
    Variable, Assignment, Logical
from PyLOX.statements import Stmt, Var, Print, Expression, Block, If, While, \
    Break
from PyLOX.token import TokenType, Token


def format_type(types):
    return "({inner})".format(inner=", ".join(map(lambda t: "<{t}>".format(t=t),
                                                  types)))


def type_check(fn=None, *, types=(float,)):
    if fn is None:
        return partial(type_check, types=types)

    expected_type_message = format_type(types)

    @wraps(fn)
    def wrapped(self, operator, *args):
        for expected_type, arg in zip(types, args):
            if type(arg) != expected_type:
                received_type_message = format_type(type(arg) for arg in args)
                raise PyLOXRuntimeError(operator, "{operator} was expecting "
                                                  "{expected} instead received "
                                                  "{given}".format(
                    operator=operator.type,
                    expected=expected_type_message,
                    given=received_type_message))
        return fn(self, operator, *args)

    return wrapped


class Interpreter(object):
    def __init__(self, stream):
        self.environment = Environment()
        self.stream = stream

    def interpret(self, expr: Stmt):
        return expr.visit(self)

    # main logic
    def visit_var(self, stmt: Var) -> None:
        name = stmt.name
        if stmt.value is None:
            value = None
        else:
            value = stmt.value.visit(self)
        self.environment.define(name, value)

    def visit_block(self, stmt: Block) -> None:
        self.execute_block(stmt.statements, Environment(self.environment))

    def execute_block(self, stmts: List[Stmt], environment: Environment) -> None:
        old_environment = self.environment
        self.environment = environment
        try:
            for stmt in stmts:
                self.interpret(stmt)
        finally:
            self.environment = old_environment

    def visit_print(self, stmt: Print) -> None:
        value = stmt.expression.visit(self)
        if value is None:
            print("nil", file=self.stream)
        else:
            if isinstance(value, float):
                value = str(value)
                if value[-2:] == ".0":
                    value = value[:-2]
            print(value, file=self.stream)

    def visit_expression(self, stmt: Expression) -> object:
        return stmt.expression.visit(self)

    def visit_if(self, stmt: If) -> object:
        if self.is_true(stmt.condition.visit(self)):
            return stmt.then_statement.visit(self)
        elif stmt.else_statement is None:
            return None
        return stmt.else_statement.visit(self)

    def visit_while(self, stmt: While) -> object:
        result = None
        while self.is_true(stmt.condition.visit(self)):
            try:
                result = stmt.body.visit(self)
            except PyLOXRuntimeError as e:
                if e.token != TokenType.BREAK:
                    raise e
                break
        return result

    def visit_break(self, stmt: Break):
        raise PyLOXRuntimeError(stmt.token, "break statement seen outside of "
                                            "a loop")

    def visit_variable(self, expr: Variable) -> object:
        return self.environment[expr.name]

    def visit_assignment(self, expr: Assignment) -> object:
        value = expr.value.visit(self)
        self.environment.assign(expr.name, value)
        return value

    def visit_logical(self, expr: Logical) -> object:
        l_value = expr.left.visit(self)
        if expr.operator == TokenType.OR:
            if self.is_true(l_value):
                return l_value
            return expr.right.visit(self)
        if expr.operator == TokenType.AND:
            if not self.is_true(l_value):
                return l_value
            return expr.right.visit(self)

    def visit_binary(self, expr: Binary) -> object:
        operators = {
            TokenType.MINUS: self.subtraction,
            TokenType.PLUS: self.addition,
            TokenType.SLASH: self.division,
            TokenType.STAR: self.multiplication,
            TokenType.GREATER_EQUAL: self.greater_equal,
            TokenType.GREATER: self.greater,
            TokenType.LESS_EQUAL: self.less_equal,
            TokenType.LESS: self.less,
            TokenType.EQUAL_EQUAL: self.equal,
            TokenType.BANG_EQUAL: self.not_equal,

        }
        op = operators.get(expr.operator, self.not_implemented)
        lhs = expr.left.visit(self)
        rhs = expr.right.visit(self)
        return op(expr.operator, lhs, rhs)

    def visit_grouping(self, expr: Grouping) -> object:
        return expr.expression.visit(self)

    def visit_literal(self, expr: Literal) -> object:
        return expr.value

    def visit_unary(self, expr: Unary) -> object:
        operators = {
            TokenType.MINUS: self.unary_minus,
            TokenType.BANG: self.binary_negation,
        }

        op = operators.get(expr.operator, self.not_implemented)

        inner = expr.right.visit(self)
        return op(expr.operator, inner)

    # helper functions
    def is_true(self, value: object) -> bool:
        if value is None or value is False:
            return False
        return True

    def not_implemented(self, operator, *args) -> None:
        raise PyLOXRuntimeError(operator, "unary operator {operator} is not "
                                          "implemented".format(operator=operator))

    # unary functions
    @type_check
    def unary_minus(self, operator: Token, inner: float) -> float:
        return -inner

    @type_check
    def binary_negation(self, operator: Token, inner: object) -> bool:
        return not self.is_true(inner)

    # binary functions
    @type_check(types=[float, float])
    def subtraction(self, operator: Token, lhs: float, rhs: float) -> float:
        return lhs - rhs

    def addition(self, operator: Token, lhs: object, rhs: object) -> object:
        if isinstance(lhs, float) and isinstance(rhs, float):
            return lhs + rhs
        if isinstance(lhs, str) and isinstance(rhs, str):
            return lhs + rhs

        raise PyLOXRuntimeError(operator, "PLUS was expecting (float, float) or "
                                          "(str, str) instead found ({lhs}, "
                                          "{rhs})".format(lhs=type(lhs),
                                                          rhs=type(rhs)))

    @type_check(types=[float, float])
    def multiplication(self, operator: Token, lhs: float, rhs: float) -> float:
        return lhs * rhs

    @type_check(types=[float, float])
    def division(self, operator: Token, lhs: float, rhs: float) -> float:
        if rhs == 0:
            raise PyLOXRuntimeError(operator, "Zero division error")
        return lhs / rhs

    @type_check(types=[float, float])
    def greater(self, operator: Token, lhs: object, rhs: object) -> bool:
        return lhs > rhs

    @type_check(types=[float, float])
    def greater_equal(self, operator: Token, lhs: object, rhs: object) -> bool:
        return lhs >= rhs

    @type_check(types=[float, float])
    def less(self, operator: Token, lhs: object, rhs: object) -> bool:
        return lhs < rhs

    @type_check(types=[float, float])
    def less_equal(self, operator: Token, lhs: object, rhs: object) -> bool:
        return lhs <= rhs

    def not_equal(self, operator: Token, lhs: object, rhs: object) -> bool:
        return not self.equal(operator, lhs, rhs)

    def equal(self, operator: Token, lhs: object, rhs: object) -> bool:
        return lhs == rhs
