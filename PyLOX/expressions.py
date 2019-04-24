from PyLOX.token import Token


class Expr(object):
    def visit(self, visitor, *args, **kwargs):
        pass


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_binary(self, *args, **kwargs)


class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_grouping(self, *args, **kwargs)


class Literal(Expr):
    def __init__(self, value: object):
        self.value = value

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_literal(self, *args, **kwargs)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_unary(self, *args, **kwargs)


class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_variable(self, *args, **kwargs)


class Assignment(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_assignment(self, *args, **kwargs)


class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def visit(self, visitor, *args, **kwargs):
        return visitor.visit_logical(self, *args, **kwargs)
