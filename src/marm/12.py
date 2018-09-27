class Statement(Node):
    pass


class StatementReturn(Statement):
    pass


class StatementWhile(Statement):
    def __init__(self, boolex, statement):
        self.boolex = boolex
        self.statement = statement


class StatementIf(Statement):
    def __init__(self, boolex, statement, elseprod):
        self.boolex = boolex
        self.statement = statement
        self.elseprod = elseprod


class StatementExpression(Statement):
    def __init__(self, expr):
        self.expr = expr


class StatementBody(Statement):
    def __init__(self, body):
        self.body = body


class StatementBreak(Statement):
    pass


class StatementContinue(Statement):
    pass
