from typing import List

from PyLOX.expressions import Binary, Grouping, Literal, Unary, \
    Variable, Assignment, Logical
from PyLOX.statements import Stmt, Var, Print, Expression, Block, If, While, \
    Break


class ExpressionPrinter(object):
    def print(self, program: List[Stmt]):
        for stmt in program:
            stmt.visit(self, 0)

    def _print(self, depth: int, *msg):
        if depth > 0:
            print((depth - 1) * " ", *msg)
        else:
            print(*msg)

    def visit_var(self, stmt: Var, depth: int):
        self._print(depth, "Variable declaration:", stmt.name)
        if stmt.value is not None:
            stmt.value.visit(self, depth + 1)

    def visit_expression(self, stmt: Expression, depth: int):
        self._print(depth, "Expression statement:")
        stmt.expression.visit(self, depth + 1)

    def visit_print(self, stmt: Print, depth: int):
        self._print(depth, "Print statement:")
        stmt.expression.visit(self, depth + 1)

    def visit_block(self, stmt: Block, depth: int):
        self._print(depth, "Block:")
        for child_stmt in stmt.statements:
            child_stmt.visit(self, depth + 1)

    def visit_if(self, stmt: If, depth: int):
        self._print(depth, "If:")
        stmt.condition.visit(self, depth + 1)
        stmt.then_statement.visit(self, depth + 1)
        if stmt.else_statement is not None:
            stmt.else_statement.visit(self, depth + 1)

    def visit_while(self, stmt: While, depth: int):
        self._print(depth, "While:")
        stmt.condition.visit(self, depth + 1)
        stmt.body.visit(self, depth + 1)

    def visit_back(self, stmt: Break, depth: int):
        self._print(depth, "Break")

    def visit_logical(self, expr: Logical, depth: int):
        self._print(depth, "Logical:")
        expr.left.visit(self, depth + 1)
        expr.right.visit(self, depth + 1)

    def visit_assignment(self, expr: Assignment, depth: int):
        self._print(depth, "Assignment", expr.name)
        expr.value.visit(self, depth + 1)

    def visit_variable(self, expr: Variable, depth: int):
        self._print(depth, "Variable", expr.name)

    def visit_binary(self, expr: Binary, depth: int):
        self._print(depth, "Binary expression:", expr.operator.type)
        expr.left.visit(self, depth + 1)
        expr.right.visit(self, depth + 1)

    def visit_grouping(self, expr: Grouping, depth: int):
        self._print(depth, "Grouping:")
        expr.expression.visit(self, depth + 1)

    def visit_literal(self, expr: Literal, depth: int):
        self._print(depth, "Literal:", expr.value)

    def visit_unary(self, expr: Unary, depth: int):
        self._print(depth, "Unary:", expr.operator.type)
        expr.right.visit(self, depth + 1)
