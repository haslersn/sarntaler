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
        elif self.op in ['+', '-', '*', '/']:
            if self.left.marm_type != 'int':
                errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                           "Left operand of {} exspects value of type int, got {}".format(
                                               self.op, self.left.marm_type))
            if self.right.marm_type != 'int':
                errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                           "Right operand of {} exspects value of type int, got {}".format(
                                               self.op, self.right.marm_type))
            self.marm_type = 'int'



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


class CreateExpr(Expr):
    def __init__(self, params):
        super().__init__()
        self.params = params

    def __str__(self):
        return "[CreateExpr: params={}]".format(self.liststr(self.params))

    def analyse_scope(self, scope_list, errorhandler):
        for param in self.params:
            param.analyse_scope(scope_list, errorhandler)

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
        pass # TODO


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
        self.lenv_depth = len(scope_list)

    def typecheck(self, errorhandler):
        self.marm_type = self.definition.get_marm_type_for(self.ident)

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


class Translationunit(Node):
    """ Non terminal 0 """
    def __init__(self, procdecllist):
        super().__init__()
        self.procs = procdecllist

    def __str__(self):
        return "[Translationunit: procs=" + self.liststr(self.procs) + "]"

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

class Proctype():
    def __init__(self, return_type, param_types):
        self.return_type = return_type
        self.param_types = param_types

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


class StatementBreak(Statement):
    """ p_statementBREAK """
    def __init__(self):
        super().__init__()
        pass

    def __str__(self):
        return "[StatementBreak]"

    def analyse_scope(self, scope_list, errorhandler): pass

    def typecheck(self, errorhandler): pass


class StatementContinue(Statement):
    """ p_statementCONTINUE """
    def __init__(self):
        super().__init__()
        pass

    def __str__(self):
        return "[StatementContinue]"

    def analyse_scope(self, scope_list, errorhandler): pass

    def typecheck(self, errorhandler): pass


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
        self.marm_type = 'bool'


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
        self.marm_type = 'bool'
