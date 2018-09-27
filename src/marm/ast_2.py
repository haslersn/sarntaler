class Node:
    pass


class Expr(Node):
    ''' Non terminal 13 (ABC) '''
    def __init__(self):
        pass


class ConstExpr(Expr):
    ''' p_expr '''
    def __init__(self, value):
        super().__init__()
        self.value = value


class BinExpr(Expr):
    ''' p_exprBINARYEXPRESSIONS '''
    def __init__(self, op, left, right):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right


class UnaryExpr(Expr):
    ''' p_exprUNARYEXPRESSIONS '''
    def __init__(self, op, operand):
        super().__init__()
        self.op = op
        self.operand = operand


class LHSExpr(Expr):
    ''' p_exprLHS '''
    def __init__(self, lhs):
        super().__init__()
        self.lhs = lhs


class StructExpr(Expr):
    ''' p_exprSTRUCTACCESS '''
    def __init__(self, expr, ident):
        super().__init__()
        self.expr = expr
        self.ident = ident


