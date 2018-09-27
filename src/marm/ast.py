class Node:
    pass


class Expr(Node):
    """ Non terminal 13 """
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
    def __init__(self, typee):
        self.typee = typee


class Translationunit(Node):
    """ Non terminal 0 """
    def __init__(self, procdecl):
        self.proc = procdecl


class Paramdecl(Node):
    """ Non terminal 3 """
    def __init__(self, param_type, name):
        self.param_type = param_type
        self.name = name


class Procdecl(Node):
    """ Non terminal 4 """
    def __init__(self, return_type, name, params, body):
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body


class Statement(Node):
    """ Non terminal 12 """
    def __init__(self):
        super().__init__()
        pass


class StatementDecl(Statement):
    """ p_statementDECL """
    def __init__(self, typee, decllist):
        super().__init__()
        self.typee = typee
        self.decllist = decllist


class StatementReturn(Statement):
    """ p_statementRETURN """
    def __init__(self, return_value):
        super().__init__()
        self.return_value = return_value
        pass


class StatementWhile(Statement):
    """ p_statementLOOPS """
    def __init__(self, boolex, statement):
        super().__init__()
        self.boolex = boolex
        self.statement = statement


class StatementIf(Statement):
    """ p_statementBRANCHING """
    def __init__(self, boolex, statement, elseprod):
        super().__init__()
        self.boolex = boolex
        self.statement = statement
        self.elseprod = elseprod


class StatementExpression(Statement):
    """ p_statementEXPRESSIONSTATEMENT """
    def __init__(self, expr):
        super().__init__()
        self.expr = expr


class StatementBody(Statement):
    """ p_body """
    def __init__(self, body):
        super().__init__()
        self.body = body


class StatementBreak(Statement):
    """ p_statementBREAK """
    def __init__(self):
        super().__init__()
        pass


class StatementContinue(Statement):
    """ p_statementCONTINUE """
    def __init__(self):
        super().__init__()
        pass


class Boolex(Node):
    """ Non terminal 15 """
    def __init__(self, op):
        super().__init__()
        self.op = op


class BoolexCMP(Boolex):
    """ p_boolexCOMPARE """
    def __init__(self, op, left, right):
        super().__init__(op)
        self.left = left
        self.right = right


class BoolexBinary(Boolex):
    """ p_boolexBINARY """
    def __init__(self, op, left, right):
        super().__init__(op)
        self.left = left
        self.right = right


class BoolexNot(Boolex):
    """ p_boolexUNARY """
    def __init__(self, op, operand):
        super().__init__(op)
        self.operand = operand

