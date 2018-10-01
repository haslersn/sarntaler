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
        """Act differently for ASSIGN expressions and mathematical operations """
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
                code += code_right
            else:
                # got an expression on the left side like a+b, which we don't want to allow
                print("BinaryExpression.code_gen: got a binary expression like a+b = 5 which we don't want to allow")
        else:
            code_left = self.left.code_gen()
            code_right = self.right.code_gen()
            """Push code_left on stack, then code_right and afterwards the operator """
            code += code_left
            code += code_right
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
        """Act differently on hash and negation, although hash is not yet implemented"""
        code = []
        if str(self.op) == "HASH":
            pass  # TODO change when the hashing is decided
        elif str(self.op) == "SUBOP":
            code_operand = self.operand.code_gen()
            code += code_operand
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
        """Pushes the address of the identifier stored in the lhs"""
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
        """TODO has not yet been decided what this should actuall do"""
        code = []
        return code


class LHS(Node):
    """ Non terminal 14 """
    def __init__(self, ident):
        super().__init__()
        self.ident = ident

    def __str__(self):
        return "[LHS: ident=" + str(self.ident) + "]"

    def code_gen(self):
        """Pushes the address of the identifier from the symbol table on the stack"""
        code = []
        ident_addr = ""  # TODO get address from symbol table
        code.append(ident_addr)
        return code


class Typename(Node):
    """ Non terminal 18 """
    def __init__(self, typee):
        super().__init__()
        self.typee = typee

    def __str__(self):
        return "[Typename: typee=" + str(self.typee) + "]"

    def code_gen(self):
        """Should not be used at all, fails on call"""
        raise NotImplementedError


class Translationunit(Node):
    """ Non terminal 0 """
    def __init__(self, procdecllist):
        super().__init__()
        self.procs = procdecllist

    def __str__(self):
        return "[Translationunit: procdecls=" + self.liststr(self.procs) + "]"

    def code_gen(self):
        """Calls codegen for every procedure and stores their addresses before"""
        code = []
        for procdecl in self.procs:
            # TODO do something with the address of the procedure
            code_proc = procdecl.code_gen()
            code += code_proc
        return code


class Paramdecl(Node):
    """ Non terminal 3 """
    def __init__(self, param_type, name):
        super().__init__()
        self.param_type = param_type
        self.name = name

    def __str__(self):
        return "[Paramdecl: param_type=" + str(self.param_type) + ", name=" + str(self.name) + "]"

    def code_gen(self):
        """Insert the identifier in the symboltable(?) and or do nothing I guess"""
        code = []
        # TODO decide if this method should do anything at all
        return code


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

    def code_gen(self):
        """Insert the identifiers in the symboltable(?) and generate the code for the body"""
        code = []
        # TODO decide what to do with the procedure and params addresses
        code_body = self.body.code_gen()
        code += code_body
        return code


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

    def code_gen(self):
        """Ignore the type and call code_gen on all declarations, whatever they may do"""
        code = []
        for decl in self.decllist:
            code += decl.code_gen()
        return code


class StatementReturn(Statement):
    """ p_statementRETURN """
    def __init__(self, return_value):
        super().__init__()
        self.return_value = return_value
        pass

    def __str__(self):
        return "[StatementReturn: return_value=" + str(self.return_value) + "]"

    def code_gen(self):
        """Push the return value and do OP_RET"""
        code = [self.return_value.code_gen(), "OP_RET"]
        return code


class StatementWhile(Statement):
    """ p_statementLOOPS """
    def __init__(self, boolex, statement):
        super().__init__()
        self.boolex = boolex
        self.statement = statement

    def __str__(self):
        return "[StatementWhile: boolex=" + str(self.boolex) + ", statement=" + str(self.statement) + "]"

    def code_gen(self):
        """First gets the bool, then negates it and jumps to end if loop is done. If not it does the body code.
        TODO change to labels!"""
        code = []
        code_boolex = self.boolex.code_gen()
        code_body = self.statement.code_gen()

        # Get the bool
        code += code_boolex
        code.append("OP_NOT")

        # Test the bool and jump accordingly (length of body + jump further + push of jump back + jump back)
        code.append(str(code_body.__len__ + 4))  # TODO test where this jumps to
        code.append("OP_JUMPRC")

        # The loop body
        code += code_body

        # Jump back to the start (length of body, bool and this jumps length +
        # jump further + length of jump further + not)
        code.append(str(-1 * (code_boolex.__len__ + code_body.__len__ + 4)))  # TODO test where this jumps to
        code.append("OP_JUMPR")
        return code


class StatementIf(Statement):
    """ p_statementBRANCHING """
    def __init__(self, boolex, statement, elseprod):
        super().__init__()
        self.boolex = boolex
        self.statement = statement
        self.elseprod = elseprod

    def __str__(self):
        return "[StatementIf: boolex={}, statement={}, elseprod={}]".format(self.boolex, self.statement, self.elseprod)

    def code_gen(self):
        """First the else block because less code, jumping accordingly TODO change to labels!"""
        code = []
        code_boolex = self.boolex.code_gen()
        code_true = self.statement.code_gen()
        code_false = self.elseprod.code_gen()

        # Get the bool
        code += code_boolex

        # Test the bool and jump accordingly (length of false body + jump further)
        code.append(str(code_false.__len__ + 1))  # TODO test where this jumps to
        code.append("OP_JUMPRC")

        # The false body
        code += code_false

        # The true body
        code += code_true

        return code


class StatementExpression(Statement):
    """ p_statementEXPRESSIONSTATEMENT """
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

    def __str__(self):
        return "[StatementExpression: expr={}]".format(self.expr)

    def code_gen(self):
        """Just generate the code for the expr whatever that may be"""
        code = [self.expr.code_gen()]
        return code


class StatementBody(Statement):
    """ p_body """
    def __init__(self, body):
        super().__init__()
        self.body = body

    def __str__(self):
        return "[StatementBody: body={}]".format(self.liststr(self.body))

    def code_gen(self):
        """Generate the code for all statements in the body"""
        code = []
        for stmnt in self.body:
            code += stmnt.code_hen()
        return code


class StatementBreak(Statement):
    """ p_statementBREAK """
    def __init__(self):
        super().__init__()
        pass

    def __str__(self):
        return "[StatementBreak]"

    def code_gen(self):
        """ TODO Need labels!!!!"""
        code = []
        return code


class StatementContinue(Statement):
    """ p_statementCONTINUE """
    def __init__(self):
        super().__init__()
        pass

    def __str__(self):
        return "[StatementContinue]"

    def code_gen(self):
        """ TODO Need labels!!!!"""
        code = []
        return code


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
        return "[BoolexCMP: op={}, left={}, right={}]".format(self.op, self.left, self.right)

    def code_gen(self):
        """Generate code for all types of comparison after executing both sides."""
        code = []
        code += self.left.code_gen()
        code += self.right.code_gen()
        if str(self.op) == "EQ":
            code.append("OP_EQ")
        elif str(self.op) == "NEQ":
            code.append("OP_EQ")
            code.append("OP_NOT")
        elif str(self.op) == "LEQ":
            code.append("OP_LE")
        elif str(self.op) == "GEQ":
            code.append("OP_GE")
        elif str(self.op) == "LT":
            code.append("OP_LT")
        elif str(self.op) == "GT":
            code.append("OP_GT")
        else:
            # we should not end up in this case
            print("BoolexCMP.code_gen: got an operator that is not valid")
        return code


class BoolexBinary(Boolex):
    """ p_boolexBINARY """
    def __init__(self, op, left, right):
        super().__init__(op)
        self.left = left
        self.right = right

    def __str__(self):
        return "[BoolexBinary: op={}, left={}, right={}]".format(self.op, self.left, self.right)

    def code_gen(self):
        """Push both sides and consume them."""
        code = []
        code += self.left.code_gen()
        code += self.right.code_gen()
        if str(self.op) == "OR":
            code.append("OP_OR")
        elif str(self.op) == "AND":
            code.append("OP_AND")
        else:
            # we should not end up in this case
            print("BoolexBinary.code_gen: got an operator that is not valid")
        return code


class BoolexNot(Boolex):
    """ p_boolexUNARY """
    def __init__(self, op, operand):
        super().__init__(op)
        self.operand = operand

    def __str__(self):
        return "[BoolexNot: operand={}]".format(str(self.operand))

    def code_gen(self):
        """Negate the result of the operand code."""
        code = []
        code += self.operand.code_gen()
        code.append("OP_NOTS")
        return code
