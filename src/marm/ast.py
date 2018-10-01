import json
import weakref


def scope_lookup(scope_list, name):
    for scope in scope_list:
        if name in scope:
            return scope[name]
    return None


class Node:
    def __init__(self):
        self.classname = self.__class__.__name__
        self.pos_filename = None
        self.pos_begin_line = None
        self.pos_end_line = None
        self.pos_begin_col = None
        self.pos_end_col = None
        self.marm_type = None

    def set_pos_from(self, p):
        (self.pos_begin_line, ignore) = p.linespan(1)
        (ignore, self.pos_end_line) = p.linespan(len(p)-1)
        from src.marm.lexer import column_number_from_lexpos
        (begin_lexpos, ignore) = p.lexspan(0)
        (ignore, end_lexpos) = p.lexspan(len(p)-1)
        self.pos_begin_col = column_number_from_lexpos(p.lexer.lexdata, begin_lexpos)
        self.pos_end_col = column_number_from_lexpos(p.lexer.lexdata, end_lexpos)
        self.pos_filename = p.lexer.filename

    def liststr(self, param):
        return "[{}]".format(", ".join(map(str,param)))

    def toJSON(self):
        def json_default(obj):
            if isinstance(obj, (weakref.ProxyType, weakref.CallableProxyType)):
                return "<weakref>"
            else:
                return obj.__dict__
        return json.dumps(self, default=json_default, sort_keys=True, indent=4)

    def _code_gen(self):
        return []

    def code_gen_with_labels(self, label_id):
        return self._code_gen()


class Expr(Node):
    """ Non terminal 13 """
    def __str__(self):
        return "[Expr]"


class SpecialExpression(Expr):
    """ p_exprSPECIALCONSTANTS"""
    def __init__(self,value):
        super().__init__()
        self.value=value

    def __str__(self):
        return "[SpecialExpr: value="+str(self.value)+"]"

    def analyse_scope(self,scope_list, errorhandler): pass

    # TODO code_gen


class ConstExpr(Expr):
    """ p_expr """
    def __init__(self, value, marm_type):
        super().__init__()
        self.value = value
        self.marm_type = marm_type

    def __str__(self):
        return "[ConstExpr: value=" + str(self.value) + "]"

    def analyse_scope(self, scope_list, errorhandler): pass

    def typecheck(self, errorhandler): pass

    def _code_gen(self):
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

    def analyse_scope(self, scope_list, errorhandler):
        self.left.analyse_scope(scope_list, errorhandler)
        self.right.analyse_scope(scope_list, errorhandler)

    def typecheck(self, errorhandler):
        self.left.typecheck(errorhandler)
        self.right.typecheck(errorhandler)
        if self.op == '=':
            if self.left.marm_type != self.right.marm_type:
                errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                           "Tried to assign value of type {} to variable of type {}.".format(
                                               self.right.marm_type, self.left.marm_type))
            else:
                self.marm_type = self.right.marm_type
        elif self.op in ['+', '-', '*', '/', '%']:
            if self.left.marm_type != 'int':
                errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                           "Left operand of {} exspects value of type int, got {}".format(
                                               self.op, self.left.marm_type))
            if self.right.marm_type != 'int':
                errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                           "Right operand of {} exspects value of type int, got {}".format(
                                               self.op, self.right.marm_type))
            self.marm_type = Typename('int')

    def code_gen_with_labels(self, label_id):
        """Act differently for ASSIGN expressions and mathematical operations """
        code = []
        if str(self.op) == "ASSIGN":
            if type(self.left) == LHSExpr:
                # create rhs code
                code_right = self.right.code_gen_with_labels(label_id)
                left_stackaddress = self.left.code_gen_with_labels(label_id)
                # OP_POPABS
                operator = "OP_POPABS"

                code.append(left_stackaddress)
                code.append(operator)
                code += code_right
            else:
                # got an expression on the left side like a+b, which we don't want to allow
                print("BinExpression._code_gen: got a binary expression like a+b = 5 which we don't want to allow")
        else:
            code_left = self.left.code_gen_with_labels(label_id)
            code_right = self.right.code_gen_with_labels(label_id)
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
                print("BinExpr._code_gen: got an operator that is not valid")
        return code


class LocalcallExpr(Expr):
    def __init__(self, fnname, params):
        super().__init__()
        self.fnname = fnname
        self.params = params

    def __str__(self):
        return "[LocalcallExpr: fnname={}, params={}]".format(self.fnname,self.liststr(self.params))

    def analyse_scope(self, scope_list, errorhandler):
        self.fnname.analyse_scope(scope_list, errorhandler)
        for param in self.params:
            param.analyse_scope(scope_list, errorhandler)

    def typecheck(self, errorhandler):
        self.fnname.typecheck(errorhandler)
        if type(self.fnname.marm_type) is not Proctype:
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Trying to call expression which is not a function.")
            return
        if len(self.params) != len(self.fnname.marm_type.param_types):
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Function {} expects {} parameters but gets {}.".format(
                                           self.fnname, len(self.fnname.marm_type.param_types), len(self.params)))
            return
        for i in range(0, len(self.params)):
            param = self.params[i]
            dparam_type = self.fnname.marm_type.param_types[i]
            param.typecheck(errorhandler)
            if param.marm_type != dparam_type:
                errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                           "Parameter {} of function  must be of type {}, got {}.".format(
                                               i, dparam_type, param.marm_type))
        self.marm_type = self.fnname.marm_type.return_type

    # TODO code_gen


class CreateExpr(Expr):
    def __init__(self, params):
        super().__init__()
        self.params = params

    def __str__(self):
        return "[CreateExpr: params={}]".format(self.liststr(self.params))

    def analyse_scope(self, scope_list, errorhandler):
        for param in self.params:
            param.analyse_scope(scope_list, errorhandler)

    # TODO code_gen


class UnaryExpr(Expr):
    """ p_exprUNARYEXPRESSIONS """
    def __init__(self, op, operand):
        super().__init__()
        self.op = op
        self.operand = operand

    def __str__(self):
        return "[UnaryExpr: op=" + str(self.op) + ", operand=" + str(self.operand) + "]"

    def analyse_scope(self, scope_list, errorhandler):
        self.operand.analyse_scope(scope_list, errorhandler)

    def typecheck(self, errorhandler):
        self.operand.typecheck(errorhandler)
        if self.op == '#':
            pass # TODO
        elif self.op == '-':
            if self.operand.marm_type != 'int':
                errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                           "Operator '-' expects one argument of type int.")
            else:
                self.marm_type = 'int'
        else:
            errorhandler.registerFatal(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Typechecking failed on unknown operator {}".format(self.op))
    def code_gen_with_labels(self, label_id):
        """Act differently on hash and negation, although hash is not yet implemented"""
        code = []
        if str(self.op) == "HASH":
            pass  # TODO change when the hashing is decided
        elif str(self.op) == "SUBOP":
            code_operand = self.operand.code_gen_with_labels(label_id)
            code += code_operand
            code.append("OP_NEG")
        else:
            # we should not end up in this case
            print("UnaryExpr._code_gen: got an operator that is not valid")
        return code


class LHSExpr(Expr):
    """ p_exprLHS """
    def __init__(self, lhs):
        super().__init__()
        self.lhs = lhs

    def __str__(self):
        return "[LHSExpr: lhs=" + str(self.lhs) + "]"

    def analyse_scope(self, scope_list, errorhandler):
        self.lhs.analyse_scope(scope_list, errorhandler)

    def typecheck(self, errorhandler):
        self.lhs.typecheck(errorhandler)

    def code_gen_with_labels(self, label_id):
        """Pushes the address of the identifier stored in the lhs"""
        return self.lhs.code_gen_with_labels(label_id)


class StructExpr(Expr):
    """ p_exprSTRUCTACCESS """
    def __init__(self, expr, ident):
        super().__init__()
        self.expr = expr
        self.ident = ident

    def __str__(self):
        return "[StructExpr: expr=" + str(self.expr) + ", ident=" + str(self.ident) + "]"

    def analyse_scope(self, scope_list, errorhandler):
        self.expr.analyse_scope(scope_list,errorhandler)
        # TODO: Attributes?

    def typecheck(self, errorhandler):
        self.expr.typecheck(errorhandler)
        if not self.expr.marm_type.has_attribute(self.ident):
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Value of type {} has not attribute named {}".format(
                                           self.expr.marm_type, self.ident))

    def _code_gen(self):
        """TODO has not yet been decided what this should actually do"""
        code = []
        return code


class LHS(Node):
    """ Non terminal 14 """
    def __init__(self, ident):
        super().__init__()
        self.ident = ident
        self.definition = None
        self.lenv_depth = None

    def __str__(self):
        return "[LHS: ident=" + str(self.ident) + "]"

    def analyse_scope(self, scope_list, errorhandler):
        self.definition = scope_lookup(scope_list, self.ident)
        if self.definition is None:
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Use of undeclared identifier {}.".format(self.ident))
        self.lenv_depth = len(scope_list)

    def typecheck(self, errorhandler):
        self.marm_type = self.definition.get_marm_type_for(self.ident)

    def _code_gen(self):
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

    def __eq__(self, other):
        if type(other) is Typename:
            return self.typee == other.typee
        elif type(other) is str: # TODO: replace with better mechanism
            return self.typee == other
        else: return False

    def _code_gen(self):
        """Should not be used at all, fails on call"""
        raise NotImplementedError

    def has_attribute(self, ident):
        return False # TODO


class Translationunit(Node):
    """ Non terminal 0 """
    def __init__(self, contractdata, procdecllist):
        super().__init__()
        self.procs = procdecllist
        self.contractdata =  contractdata

    def __str__(self):
        return "[Translationunit: contractdata = "+str(self.contractdata)+" procs=" + self.liststr(self.procs) + "]"

    def analyse_scope(self, scope_list=[], errorhandler=None):
        local_scope_list = [{}]+scope_list
        for proc in self.procs:
            local_scope_list[0][proc.name] = proc
        for proc in self.procs:
            proc.analyse_scope(local_scope_list, errorhandler)

    def typecheck(self, errorhandler):
        for proc in self.procs:
            proc.set_global_definition_types(errorhandler)
        for proc in self.procs:
            proc.typecheck(errorhandler)

    def code_gen_with_labels(self, label_id):
        """Calls codegen for every procedure and stores their addresses before"""
        code = []
        for procdecl in self.procs:
            # TODO do something with the address of the procedure
            code_proc = procdecl.code_gen_with_labels(label_id)
            code += code_proc
        return code


class Paramdecl(Node):
    """ Non terminal 3 """
    def __init__(self, param_type, name):
        super().__init__()
        self.param_type = param_type
        self.name = name
        self.local_var_index = None
        self.lenv_depth = None
        self.marm_type = self.param_type

    def __str__(self):
        return "[Paramdecl: param_type=" + str(self.param_type) + ", name=" + str(self.name) + "]"

    def analyse_scope(self, scope_list, errorhandler):
        if self.name in scope_list[0]:
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Multiple parameters have the name {}.".format(self.name)) #TODO
        self.local_var_index = len(scope_list[0])
        self.lenv_depth = len(scope_list)
        scope_list[0][self.name] = self

    def typecheck(self, errorhandler): pass

    def get_marm_type_for(self, ident):
        assert(ident == self.name)
        return self.param_type

    def _code_gen(self):
        """Insert the identifier in the symboltable(?) and or do nothing I guess"""
        code = []
        # TODO decide if this method should do anything at all
        return code


class Proctype():
    def __init__(self, return_type, param_types):
        self.return_type = return_type
        self.param_types = param_types

    def has_attribute(self, ident):
        return False


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

    def analyse_scope(self, scope_list, errorhandler):
        local_scope_list = [{"#current_function": self}] + scope_list
        for param in self.params:
            param.analyse_scope(local_scope_list, errorhandler)
        for statement in self.body:
            statement.analyse_scope(local_scope_list, errorhandler)

    def get_marm_type_for(self, ident):
        assert(self.name == ident)
        return self.marm_type

    def set_global_definition_types(self, errorhandler):
        param_types = []
        for param in self.params:
            param.typecheck(errorhandler)
            param_types.append(param.marm_type)
        self.marm_type = Proctype(self.return_type, param_types)

    def typecheck(self, errorhandler):
        for statement in self.body:
            statement.typecheck(errorhandler)

    def code_gen_with_labels(self, label_id):
        """Insert the identifiers in the symboltable(?) and generate the code for the body"""
        code = []
        # TODO decide what to do with the procedure and params addresses
        code_body = self.body.code_gen_with_labels(label_id)
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
        self.local_var_indices = None
        self.lenv_depth = None

    def __str__(self):
        return "[StatementDecl: typee=" + str(self.typee) + ", decllist=" + self.liststr(self.decllist) + "]"

    def analyse_scope(self, scope_list, errorhandler):
        self.local_var_indices = {}
        self.lenv_depth = len(scope_list)
        for decl in self.decllist:
            if decl in scope_list[0]:
                errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                           "Variable {} declared twice".format(decl)) #TODO
            self.local_var_indices[decl] = len(scope_list[0])
            scope_list[0][decl] = self

    def get_marm_type_for(self, ident):
        return self.typee

    def typecheck(self, errorhandler): pass

    def code_gen_with_labels(self, label_id):
        """Ignore the type and call _code_gen on all declarations, whatever they may do"""
        code = []
        for decl in self.decllist:
            code += decl.code_gen_with_labels(label_id)
        return code


class StatementReturn(Statement):
    """ p_statementRETURN """
    def __init__(self, return_value):
        super().__init__()
        self.return_value = return_value
        pass

    def __str__(self):
        return "[StatementReturn: return_value=" + str(self.return_value) + "]"

    def analyse_scope(self, scope_list, errorhandler):
        self.function = weakref.proxy(scope_lookup(scope_list, "#current_function"))
        self.return_value.analyse_scope(scope_list, errorhandler)

    def typecheck(self, errorhandler):
        self.return_value.typecheck(errorhandler)
        if self.return_value.marm_type != self.function.marm_type.return_type:
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Can't return value of type {} from function with return type {}".format(
                                           self.return_value.marm_type, self.function.marm_type.return_type))
        # TODO

    def code_gen_with_labels(self, label_id):
        """Push the return value and do OP_RET"""
        code = [self.return_value.code_gen_with_labels(label_id), "OP_RET"]
        return code


class StatementWhile(Statement):
    """ p_statementLOOPS """
    def __init__(self, boolex, statement):
        super().__init__()
        self.boolex = boolex
        self.statement = statement

    def __str__(self):
        return "[StatementWhile: boolex=" + str(self.boolex) + ", statement=" + str(self.statement) + "]"

    def analyse_scope(self, scope_list, errorhandler):
        self.boolex.analyse_scope(scope_list, errorhandler)
        self.statement.analyse_scope(scope_list, errorhandler)

    def typecheck(self, errorhandler):
        self.statement.typecheck(errorhandler)

        def _code_gen(self):
            pass

        def code_gen_with_labels(self, label_id):
            """First gets the bool, then negates it and jumps to end if loop is done. If not it does the body code."""
            code = []
            code_boolex = self.boolex.code_gen_with_labels(label_id + 1)
            code_body = self.statement.code_gen_with_labels(label_id + 1)

            label_start = "__label_loop_start" + str(label_id)
            label_end = "__label_loop_end" + str(label_id)

            # Start label
            code.append(label_start)

            # Get the bool
            code += code_boolex
            code.append("OP_NOT")

            # TODO jump to label_end
            code.append("OP_JUMPRC")

            # The loop body
            code += code_body

            # TODO Jump to label_start
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
        return "[StatementIf: boolex={}, statement={}, elseprod={}]".format(self.boolex,self.statement,self.elseprod)

    def analyse_scope(self, scope_list, errorhandler):
        self.boolex.analyse_scope(scope_list, errorhandler)
        self.statement.analyse_scope(scope_list, errorhandler)
        if not (self.elseprod is None):
            self.elseprod.analyse_scope(scope_list, errorhandler)

    def typecheck(self, errorhandler):
        self.boolex.typecheck(errorhandler)
        if self.boolex.marm_type != 'bool':
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Condition in an if statement must be of type bool.")
        self.statement.typecheck(errorhandler)
        self.statement.typecheck(errorhandler)

    def _code_gen(self):
        pass

    def code_gen_with_labels(self, label_id):
        """First the else block because less code, jumping accordingly"""
        code = []
        code_boolex = self.boolex.code_gen_with_labels(label_id + 1)
        code_true = self.statement.code_gen_with_labels(label_id + 1)
        code_false = self.elseprod.code_gen_with_labels(label_id + 1)

        # Label of true block
        label_true = "__label_if_true" + str(label_id)

        # Get the bool
        code += code_boolex

        # TODO Jump to true label
        code.append("OP_JUMPRC")

        # The false body
        code += code_false

        code.append(label_true)

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

    def analyse_scope(self, scope_list, errorhandler):
        self.expr.analyse_scope(scope_list, errorhandler)

    def typecheck(self, errorhandler):
        self.expr.typecheck(errorhandler)

    def code_gen_with_labels(self, label_id):
        """Just generate the code for the expr whatever that may be"""
        code = [self.expr.code_gen_with_labels(label_id)]
        return code


class StatementBody(Statement):
    """ p_body """
    def __init__(self, body):
        super().__init__()
        self.body = body

    def __str__(self):
        return "[StatementBody: body={}]".format(self.liststr(self.body))

    def analyse_scope(self, scope_list, errorhandler):
        local_scope_list = [{}] + scope_list
        for statement in self.body:
            statement.analyse_scope(local_scope_list, errorhandler)

    def typecheck(self, errorhandler):
        for statement in self.body:
            statement.typecheck(errorhandler)

    def _code_gen(self):
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

    def analyse_scope(self, scope_list, errorhandler): pass

    def typecheck(self, errorhandler): pass

    def _code_gen(self):
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

    def analyse_scope(self, scope_list, errorhandler): pass

    def typecheck(self, errorhandler): pass

    class StatementContinue(Statement):
        """ p_statementCONTINUE """

        def __init__(self):
            super().__init__()
            pass

        def __str__(self):
            return "[StatementContinue]"

        def _code_gen(self):
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
        return "[BoolexCMP: op={}, left={}, right={}]".format(self.op,self.left,self.right)

    def analyse_scope(self, scope_list, errorhandler):
        self.left.analyse_scope(scope_list, errorhandler)
        self.right.analyse_scope(scope_list, errorhandler)

    def typecheck(self, errorhandler):
        self.left.typecheck(errorhandler)
        self.right.typecheck(errorhandler)
        if self.left.marm_type != self.right.marm_type:
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Trying to compare values of types {} and {}.".format(
                                           self.left.marm_type, self.right.marm_type))
        # TODO
        self.marm_type = 'bool'

    def code_gen_with_labels(self, label_id):
        """Generate code for all types of comparison after executing both sides."""
        code = []
        code += self.left.code_gen_with_labels(label_id)
        code += self.right.code_gen_with_labels(label_id)
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
            print("BoolexCMP._code_gen: got an operator that is not valid")
        return code


class BoolexBinary(Boolex):
    """ p_boolexBINARY """
    def __init__(self, op, left, right):
        super().__init__(op)
        self.left = left
        self.right = right

    def __str__(self):
        return "[BoolexBinary: op={}, left={}, right={}]".format(self.op,self.left,self.right)

    def analyse_scope(self, scope_list, errorhandler):
        self.left.analyse_scope(scope_list, errorhandler)
        self.right.analyse_scope(scope_list, errorhandler)

    def typecheck(self, errorhandler):
        self.left.typecheck(errorhandler)
        if self.left.marm_type != 'bool':
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Left operand of {} must be of type bool.".format(
                                           self.op))
        self.right.typecheck(errorhandler)
        if self.right.marm_type != 'bool':
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Right operand of {} must be of type bool.".format(
                                           self.op))
        self.marm_type = Typename('bool')

    def code_gen_with_labels(self, label_id):
        """Push both sides and consume them."""
        code = []
        code += self.left.code_gen_with_labels(label_id)
        code += self.right.code_gen_with_labels(label_id)
        if str(self.op) == "OR":
            code.append("OP_OR")
        elif str(self.op) == "AND":
            code.append("OP_AND")
        else:
            # we should not end up in this case
            print("BoolexBinary._code_gen: got an operator that is not valid")
        return code


class BoolexNot(Boolex):
    """ p_boolexUNARY """
    def __init__(self, op, operand):
        super().__init__(op)
        self.operand = operand

    def __str__(self):
        return "[BoolexNot: operand={}]".format(str(self.operand))

    def analyse_scope(self, scope_list, errorhandler):
        self.operand.analyse_scope(scope_list, errorhandler)

    def typecheck(self, errorhandler):
        self.operand.typecheck(errorhandler)
        if self.operand.marm_type != 'bool':
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Operand of '!' needs to be of type bool.")
        self.marm_type = Typename('bool')

    def code_gen_with_labels(self, label_id):
        """Negate the result of the operand code."""
        code = []
        code += self.operand.code_gen_with_labels(label_id)
        code.append("OP_NOTS")
        return code
