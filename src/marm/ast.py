class Node:
    pass


class Expr(Node):
    """ Non terminal 13 (ABC) """
    def __init__(self):
        pass


class ConstExpr(Expr):
    """ p_expr """
    def __init__(self, value):
        super().__init__()
        self.value = value


class BinExpr(Expr):
    """ p_exprBINARYEXPRESSIONS """
    def __init__(self, op, left, right):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right


class UnaryExpr(Expr):
    """ p_exprUNARYEXPRESSIONS """
    def __init__(self, op, operand):
        super().__init__()
        self.op = op
        self.operand = operand


class LHSExpr(Expr):
    """ p_exprLHS """
    def __init__(self, lhs):
        super().__init__()
        self.lhs = lhs


class StructExpr(Expr):
    """ p_exprSTRUCTACCESS """
    def __init__(self, expr, ident):
        super().__init__()
        self.expr = expr
        self.ident = ident


class LHS(Node):
    """ Non terminal 14 """
    def __init__(self, ident):
        self.ident = ident


class Translationunit(Node):
    def __init__(self,procdecl):
        self.proc=procdecl


class Procdecl(Node):
    def __init__(self,returnType,name,params,body):
        self.returnType = returnType
        self.name = name
        self.params = params
        self.body = body


class Statement(Node):
    super().__init__()
    pass


class StatementReturn(Statement):
    super().__init__()
    pass


class StatementWhile(Statement):
    def __init__(self, boolex, statement):
        super().__init__()
        self.boolex = boolex
        self.statement = statement


class StatementIf(Statement):
    def __init__(self, boolex, statement, elseprod):
        super().__init__()
        self.boolex = boolex
        self.statement = statement
        self.elseprod = elseprod


class StatementExpression(Statement):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr


class StatementBody(Statement):
    def __init__(self, body):
        super().__init__()
        self.body = body


class StatementBreak(Statement):
    super().__init__()
    pass


class StatementContinue(Statement):
    super().__init__()
    pass


class Boolex(Node):
    def __init__(self, op):
        super().__init__()
        self.op = op


class BoolexBinary(Boolex):
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right


class BoolexNot(Boolex):
    def __init__(self, operand):
        super().__init__()
        self.operand = operand

