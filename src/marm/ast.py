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


class Typename(Node):
    """ Non terminal 18 """
    def __init__(self, type):
        self.type = type


class Translationunit(Node):
    def __init__(self, procdecl):
        self.proc = procdecl


class Paramdecl(Node):
    def __init__(self,paramType,name):
        self.paramType = paramType
        self.name = name


class Procdecl(Node):
    def __init__(self, returnType, name, params, body):
        self.returnType = returnType
        self.name = name
        self.params = params
        self.body = body


class Statement(Node):
    def __init__(self):
        super().__init__()
        pass


class StatementDecl(Statement):
    """ p_statementDECL """
    def __init__(self, type, decllist):
        super().__init__()
        self.type = type
        self.decllist = decllist


class StatementReturn(Statement):
    def __init__(self, returnValue):
        super().__init__()
        self.returnValue = returnValue


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
    def __init__(self):
        super().__init__()
        pass


class StatementContinue(Statement):
    def __init__(self):
        super().__init__()
        pass


class Boolex(Node):
    def __init__(self, op):
        super().__init__()
        self.op = op


class BoolexBinary(Boolex):
    def __init__(self, op, left, right):
        super().__init__(op)
        self.left = left
        self.right = right


class BoolexNot(Boolex):
    def __init__(self, op, operand):
        super().__init__(op)
        self.operand = operand

