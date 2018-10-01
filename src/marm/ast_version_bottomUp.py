import json


class Node:
    def __init__(self):
        self.classname = self.__class__.__name__

    def liststr(self, param):
        return "[{}]".format(", ".join(map(str, param)))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def code_gen(self):
        return []


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

    def code_gen(self):
        return [self.value]


class BinExpr(Expr):
    """ p_exprBINARYEXPRESSIONS """
    def __init__(self, op, left, right):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return "[BinExpr: op=" + str(self.op) + ", left=" + str(self.left) + ", right=" + str(self.right) + "]"

    def code_gen(self):
        """ act differently for ASSIGN expressions and mathematical operations """
        code = []
        if str(self.op) == "ASSIGN":
            if type(self.left) == LHSExpr:
                # create rhs code
                code_right = self.right.code_gen()
                left_stackaddress = self.left.code_gen()
                # OP_POPABS
                operator = "OP_POPABS"

                code.append(left_stackaddress)
                code.append(operator)
                for line in code_right:
                    code.append(line)
            else:
                # got an expression on the left side like a+b, which we don't want to allow
                print("BinaryExpression.code_gen: got a binary expression like a+b = 5 which we don't want to allow")
        else:
            code_left = self.left.code_gen()
            code_right = self.right.code_gen()
            """ push code_left on stack, then code_right and afterwards the operator """
            for line in code_left:
                code.append(line)
            for line in code_right:
                code.append(line)
            if str(self.op) == "ADDOP":
                code.append("OP_ADD")
            elif str(self.op) == "SUBOP":
                code.append("OP_SUB")
            elif str(self.op) == "MULOP":
                code.append("OP_MUL")
            elif str(self.op) == "DIVOP":
                code.append("OP_DIV")
            else:
                # we should not end up in this case
                print("BinExpr.code_gen: got an operator that is not valid")
        return code


class UnaryExpr(Expr):
    """ p_exprUNARYEXPRESSIONS """
    def __init__(self, op, operand):
        super().__init__()
        self.op = op
        self.operand = operand

    def __str__(self):
        return "[UnaryExpr: op=" + str(self.op) + ", operand=" + str(self.operand) + "]"

    def code_gen(self):
        """act differently on hash and negation, although hash is not yet implemented"""
        code = []
        if str(self.op) == "HASH":
            pass  # TODO change when the hashing is decided
        elif str(self.op) == "SUBOP":
            code_operand = self.operand.code_gen()
            for line in code_operand:
                code.append(line)
            code.append("OP_NEG")
        else:
            # we should not end up in this case
            print("UnaryExpr.code_gen: got an operator that is not valid")
        return code


class LHSExpr(Expr):
    """ p_exprLHS """
    def __init__(self, lhs):
        super().__init__()
        self.lhs = lhs

    def __str__(self):
        return "[LHSExpr: lhs=" + str(self.lhs) + "]"

    def code_gen(self):
        """pushes the address of the identifier stored in the lhs"""
        return self.lhs.code_gen()


class StructExpr(Expr):
    """ p_exprSTRUCTACCESS """
    def __init__(self, expr, ident):
        super().__init__()
        self.expr = expr
        self.ident = ident

    def __str__(self):
        return "[StructExpr: expr=" + str(self.expr) + ", ident=" + str(self.ident) + "]"

    def code_gen(self):
        """pushes the address of the identifier stored in the lhs"""
        code = []

        return code


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
    def __init__(self, procdecl):
        super().__init__()
        self.proc = procdecl

    def __str__(self):
        return "[Translationunit: procdecl=" + str(self.proc) + "]"


class Paramdecl(Node):
    """ Non terminal 3 """
    def __init__(self, param_type, name):
        super().__init__()
        self.param_type = param_type
        self.name = name

    def __str__(self):
        return "[Paramdecl: param_type=" + str(self.param_type) + ", name=" + str(self.name) + "]"


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


class StatementReturn(Statement):
    """ p_statementRETURN """
    def __init__(self, return_value):
        super().__init__()
        self.return_value = return_value
        pass

    def __str__(self):
        return "[StatementReturn: return_value=" + str(self.return_value) + "]"


class StatementWhile(Statement):
    """ p_statementLOOPS """
    def __init__(self, boolex, statement):
        super().__init__()
        self.boolex = boolex
        self.statement = statement

    def __str__(self):
        return "[StatementWhile: boolex=" + str(self.boolex) + ", statement=" + str(self.statement) + "]"


class StatementIf(Statement):
    """ p_statementBRANCHING """
    def __init__(self, boolex, statement, elseprod):
        super().__init__()
        self.boolex = boolex
        self.statement = statement
        self.elseprod = elseprod

    def __str__(self):
        return "[StatementIf: boolex={}, statement={}, elseprod={}]".format(self.boolex,self.statement,self.elseprod)


class StatementExpression(Statement):
    """ p_statementEXPRESSIONSTATEMENT """
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

    def __str__(self):
        return "[StatementExpression: expr={}]".format(self.expr)


class StatementBody(Statement):
    """ p_body """
    def __init__(self, body):
        super().__init__()
        self.body = body

    def __str__(self):
        return "[StatementBody: body={}]".format(self.liststr(self.body))


class StatementBreak(Statement):
    """ p_statementBREAK """
    def __init__(self):
        super().__init__()
        pass

    def __str__(self):
        return "[StatementBreak]"


class StatementContinue(Statement):
    """ p_statementCONTINUE """
    def __init__(self):
        super().__init__()
        pass

    def __str__(self):
        return "[StatementContinue]"


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


class BoolexBinary(Boolex):
    """ p_boolexBINARY """
    def __init__(self, op, left, right):
        super().__init__(op)
        self.left = left
        self.right = right

    def __str__(self):
        return "[BoolexBinary: op={}, left={}, right={}]".format(self.op,self.left,self.right)


class BoolexNot(Boolex):
    """ p_boolexUNARY """
    def __init__(self, op, operand):
        super().__init__(op)
        self.operand = operand

    def __str__(self):
        return "[BoolexNot: operand={}]".format(str(self.operand))
