import json

def scope_lookup(scope_list, name):
    for scope in scope_list:
        if name in scope:
            return scope[name]
    return None

class Node:
    def __init__(self):
        self.classname = self.__class__.__name__

    def liststr(self, param):
        return "[{}]".format(", ".join(map(str,param)))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class Expr(Node):
    """ Non terminal 13 """
    def __str__(self):
        return "[Expr]"


class ConstExpr(Expr):
    """ p_expr """
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return "[ConstExpr: value=" + str(self.value) + "]"


class BinExpr(Expr):
    """ p_exprBINARYEXPRESSIONS """
    def __init__(self, op, left, right):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return "[BinExpr: op=" + str(self.op) + ", left=" + str(self.left) + ", right=" + str(self.right) + "]"


class UnaryExpr(Expr):
    """ p_exprUNARYEXPRESSIONS """
    def __init__(self, op, operand):
        super().__init__()
        self.op = op
        self.operand = operand

    def __str__(self):
        return "[UnaryExpr: op=" + str(self.op) + ", operand=" + str(self.operand) + "]"


class LHSExpr(Expr):
    """ p_exprLHS """
    def __init__(self, lhs):
        super().__init__()
        self.lhs = lhs

    def __str__(self):
        return "[LHSExpr: lhs=" + str(self.lhs) + "]"


class StructExpr(Expr):
    """ p_exprSTRUCTACCESS """
    def __init__(self, expr, ident):
        super().__init__()
        self.expr = expr
        self.ident = ident

    def __str__(self):
        return "[StructExpr: expr=" + str(self.expr) + ", ident=" + str(self.ident) + "]"


class LHS(Node):
    """ Non terminal 14 """
    def __init__(self, ident):
        super().__init__()
        self.ident = ident

    def __str__(self):
        return "[LHS: ident=" + str(self.ident) + "]"


class Typename(Node):
    """ Non terminal 18 """
    def __init__(self, typee):
        super().__init__()
        self.typee = typee

    def __str__(self):
        return "[Typename: typee=" + str(self.typee) + "]"


class Translationunit(Node):
    """ Non terminal 0 """
    def __init__(self, procdecllist):
        super().__init__()
        self.procs = procdecllist

    def __str__(self):
        return "[Translationunit: procs=" + str(self.procs) + "]"


class Paramdecl(Node):
    """ Non terminal 3 """
    def __init__(self, param_type, name):
        super().__init__()
        self.param_type = param_type
        self.name = name

    def __str__(self):
        return "[Paramdecl: param_type=" + str(self.param_type) + ", name=" + str(self.name) + "]"

    def analyse_scope(self, scope_list):
        if self.name in scope_list[0]:
            print("Multiple parameters have the name {}.".format(self.name))
        scope_list[self.name] = self
        self.local_var_index = len(scope_list[0])


class Procdecl(Node):
    """ Non terminal 4 """
    def __init__(self, return_type, name, params, body):
        super().__init__()
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body

    def __str__(self):
        return "[Procdecl: return_type=" + str(self.return_type) + ", name=" + str(self.name) + ", params=" +\
               self.liststr(self.params) + ", body=" + self.liststr(self.body) + "]"

    def analyse_scope(self, scope_list):
        local_scope_list = [{}] + scope_list
        for param in self.params:
            param.analyse_scope(local_scope_list)
        for statement in self.body:
            statement.analyse_scope(local_scope_list)

class Statement(Node):
    """ Non terminal 12 """
    def __init__(self):
        super().__init__()
        pass

    def __str__(self):
        return "[Statement]"


class StatementDecl(Statement):
    """ p_statementDECL """
    def __init__(self, typee, decllist):
        super().__init__()
        self.typee = typee
        self.decllist = decllist

    def __str__(self):
        return "[StatementDecl: typee=" + str(self.typee) + ", decllist=" + self.liststr(self.decllist) + "]"

    def analyse_scope(self, scope_list):
        self.local_var_indices = {}
        for decl in decllist:
            if decl in scope_list[0]:
                print("Variable {} declared twice".format(decl)) # TODO error handling
            scope_list[decl] = self
            local_var_indices[decl] = len(scope_list[0])


class StatementReturn(Statement):
    """ p_statementRETURN """
    def __init__(self, return_value):
        super().__init__()
        self.return_value = return_value
        pass

    def __str__(self):
        return "[StatementReturn: return_value=" + str(self.return_value) + "]"

    def analyse_scope(self, scope_list):
        self.return_value.analyse_scope(scope_list)


class StatementWhile(Statement):
    """ p_statementLOOPS """
    def __init__(self, boolex, statement):
        super().__init__()
        self.boolex = boolex
        self.statement = statement

    def __str__(self):
        return "[StatementWhile: boolex=" + str(self.boolex) + ", statement=" + str(self.statement) + "]"

    def analyse_scope(self, scope_list):
        self.boolex.analyse_scope(scope_list)
        self.statement.analyse_scope(scope_list)


class StatementIf(Statement):
    """ p_statementBRANCHING """
    def __init__(self, boolex, statement, elseprod):
        super().__init__()
        self.boolex = boolex
        self.statement = statement
        self.elseprod = elseprod

    def __str__(self):
        return "[StatementIf: boolex={}, statement={}, elseprod={}]".format(self.boolex,self.statement,self.elseprod)

    def analyse_scope(self, scope_list):
        self.boolex.analyse_scope(scope_list)
        self.statement.analyse_scope(scope_list)
        if not (self.elseprod is None):
            self.elseprod.analyse_scope(scope_list)


class StatementExpression(Statement):
    """ p_statementEXPRESSIONSTATEMENT """
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

    def __str__(self):
        return "[StatementExpression: expr={}]".format(self.expr)

    def analyse_scope(self, scope_list):
        expr.analyse_scope(scope_list)


class StatementBody(Statement):
    """ p_body """
    def __init__(self, body):
        super().__init__()
        self.body = body

    def __str__(self):
        return "[StatementBody: body={}]".format(self.liststr(self.body))

    def analyse_scope(self, scope_list):
        local_scope_list = [{}] + scope_list
        for statement in body:
            statement.analyse_scope(local_scope_list)


class StatementBreak(Statement):
    """ p_statementBREAK """
    def __init__(self):
        super().__init__()
        pass

    def __str__(self):
        return "[StatementBreak]"

    def analyse_scope(self, scope_list): pass


class StatementContinue(Statement):
    """ p_statementCONTINUE """
    def __init__(self):
        super().__init__()
        pass

    def __str__(self):
        return "[StatementContinue]"

    def analyse_scope(self, scope_list): pass


class Boolex(Node):
    """ Non terminal 15 """
    def __init__(self, op):
        super().__init__()
        self.op = op

    def __str__(self):
        return "[Boolex: op={}]".format(self.op)


class BoolexCMP(Boolex):
    """ p_boolexCOMPARE """
    def __init__(self, op, left, right):
        super().__init__(op)
        self.left = left
        self.right = right

    def __str__(self):
        return "[BoolexCMP: op={}, left={}, right={}]".format(self.op,self.left,self.right)

    def analyse_scope(self, scope_list):
        self.left.analyse_scope(scope_list)
        self.right.analyse_scope(scope_list)


class BoolexBinary(Boolex):
    """ p_boolexBINARY """
    def __init__(self, op, left, right):
        super().__init__(op)
        self.left = left
        self.right = right

    def __str__(self):
        return "[BoolexBinary: op={}, left={}, right={}]".format(self.op,self.left,self.right)

    def analyse_scope(self, scope_list):
        self.left.analyse_scope(scope_list)
        self.right.analyse_scope(scope_list)


class BoolexNot(Boolex):
    """ p_boolexUNARY """
    def __init__(self, op, operand):
        super().__init__(op)
        self.operand = operand

    def __str__(self):
        return "[BoolexNot: operand={}]".format(str(self.operand))

    def analyse_scope(self, scope_list):
        self.operand.analyse_scope(scope_list)

