class Node:
    pass


class Expr(Node):
    ''' Non terminal 13 (ABC) '''
    def __init__(self):
        pass


class ConstExpr(Expr):
    ''' p_expr '''
    def __init__(self, value):
        self.value = value


class BinExpr(Expr):
    ''' p_exprBINARYEXPRESSIONS '''
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class UnaryExpr(Expr):
    ''' p_exprUNARYEXPRESSIONS '''
    def __init__(self, op, right):
        self.op = op
        self.right = right


class LHSExpr(Expr):
    ''' p_exprLHS '''
    def __init__(self, lhs):
        self.lhs = lhs