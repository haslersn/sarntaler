import json
import weakref


class Scope:
    def __init__(self, outer=None):
        self.outer = outer
        self.local_vars = {}
        self.next_var_index_delta = 0
    def define(self, name, value):
        self.local_vars[name] = value
    def lookup(self, name):
        if name in self.local_vars:
            return self.local_vars[name]
        elif self.outer is not None:
            return self.outer.lookup(name)
        else:
            return None
    def has_direct_definition(self, name):
        return name in self.local_vars
    def _next_var_index(self):
        if self.outer is None:
            return self.next_var_index_delta
        else:
            return self.next_var_index_delta + self.outer._next_var_index()
    def get_next_var_index(self):
        if self.outer is None:
            res = self.next_var_index_delta
        else:
            res = self.next_var_index_delta + self.outer._next_var_index()
        self.next_var_index_delta+=1
        return res


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

    def code_gen(self, errorhandler):
        return []


class Expr(Node):
    """ Non terminal 13 """
    def __str__(self):
        return "[Expr]"


class SpecialExpression(Expr):
    """ p_exprSPECIALCONSTANTS"""
    def __init__(self,value, marm_type):
        super().__init__()
        self.value=value
        self.marm_type = marm_type

    def __str__(self):
        return "[SpecialExpr: value="+str(self.value)+"]"

    def analyse_scope(self,scope, errorhandler): pass

    def typecheck(self, errorhandler): pass

    # TODO code_gen


class ConstExpr(Expr):
    """ p_expr """
    def __init__(self, value, marm_type):
        super().__init__()
        self.value = value
        self.marm_type = marm_type

    def __str__(self):
        return "[ConstExpr: value=" + str(self.value) + "]"

    def analyse_scope(self, scope, errorhandler): pass

    def typecheck(self, errorhandler): pass

    def code_gen(self, errorhandler):
        if self.marm_type is 'string':
            return ['"'+self.value+'" // const string']
        else:
            return [str(self.value) + ' // const '+str(self.marm_type)]


class BinExpr(Expr):
    """ p_exprBINARYEXPRESSIONS """
    def __init__(self, op, left, right):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return "[BinExpr: op=" + str(self.op) + ", left=" + str(self.left) + ", right=" + str(self.right) + "]"

    def analyse_scope(self, scope, errorhandler):
        self.left.analyse_scope(scope, errorhandler)
        self.right.analyse_scope(scope, errorhandler)

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

    def code_gen(self, errorhandler):
        """Act differently for ASSIGN expressions and mathematical operations """
        code = []
        if str(self.op) == "=":
            if type(self.left) == LHS:
                # create rhs code
                code_right = self.right.code_gen()
                left_setcode = self.left.code_gen_LHS()

                code += code_right
                code += left_setcode
            else:
                # got an expression on the left side like a+b, which we don't want to allow
                print("BinExpr.code_gen: got a binary expression like a+b = 5 which we don't want to allow")
        else:
            code_left = self.left.code_gen()
            code_right = self.right.code_gen()
            """Push code_left on stack, then code_right and afterwards the operator """
            code += code_left
            code += code_right
            if str(self.op) == "+":
                code.append("OP_ADD")
            elif str(self.op) == "-":
                code.append("OP_SUB")
            elif str(self.op) == "*":
                code.append("OP_MUL")
            elif str(self.op) == "/":
                code.append("OP_DIV")
            else:
                # we should not end up in this case
                print("BinExpr.code_gen: got an operator that is not valid")
        return code

class ContractcallExpr(Expr):
    def __init__(self, fnname, fee, params):
        super().__init__()
        self.fnname = fnname
        self.params = params
        self.fee = fee

    def __str__(self):
        return "[ContractcallExpr: fnname={}, fee={}, params={}]".format(self.fnname,self.fee,self.liststr(self.params))

    def analyse_scope(self, scope, errorhandler):
        self.fnname.analyse_scope(scope, errorhandler)
        for fees in self.fee:
            fees.analyse_scope(scope, errorhandler)
        for param in self.params:
            param.analyse_scope(scope, errorhandler)

    def typecheck(self, errorhandler):
        self.fnname.typecheck(errorhandler)
        errorhandler.registerWarning(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Warning: We currently do not check whether a contract call expression actually types.")
        if len(self.fee)!=1:
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                        "Error: Contract calls have only a single parameter for the fee part")
        for i in range(0, len(self.params)):
            param = self.params[i]
            param.typecheck(errorhandler)
        self.marm_type = Typename('generic')

    def code_gen(self, errorhandler):
        """TODO create code for inter-contract call"""
        code_methodid = self.fnname.code_gen()

        code = []
        code.append("// start construction site for TRANSFER")
        for param in self.params:#[::-1]:
            code+=param.code_gen()
        code+=code_methodid
        code.append(len(self.params)+1)
        code.append("OP_PACK // S3 == params")
        code.append("// S2 == contract address")
        for fe in self.fee:
            code+=fe.code_gen()
        code.append("// S1 == FEE")
        code.append("OP_TRANSFER")
        for param in self.params:#[::-1]:
            code.append("OP_SWAP")
            code.append("OP_POPVOID")
        code.append("// end construction site for TRANSFER")
        return code

class LocalcallExpr(Expr):
    def __init__(self, fnname, params):
        super().__init__()
        self.fnname = fnname
        self.params = params

    def __str__(self):
        return "[LocalcallExpr: fnname={}, params={}]".format(self.fnname,self.liststr(self.params))

    def analyse_scope(self, scope, errorhandler):
        self.fnname.analyse_scope(scope, errorhandler)
        for param in self.params:
            param.analyse_scope(scope, errorhandler)

    def typecheck(self, errorhandler):
        self.fnname.typecheck(errorhandler)
        if type(self.fnname.marm_type) is Proctype:
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
                    errorhandler.registerError(param.pos_filename, param.pos_begin_line, param.pos_begin_col,
                                               "Parameter {} of function must be of type {}, got {}.".format(
                                                   i, dparam_type, param.marm_type))
            self.marm_type = self.fnname.marm_type.return_type
        else:
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Trying to call expression which is not a function.")
            return
    def code_gen(self, errorhandler):
        code_methodid = self.fnname.code_gen()

        code = []
        for param in self.params:#[::-1]:
            code+=param.code_gen()
        code+=code_methodid
        code.append("OP_CALL")
        for param in self.params:#[::-1]:
            code.append("OP_SWAP")
            code.append("OP_POPVOID")
        return code


# class CreateExpr(Expr):
#     def __init__(self, params):
#         super().__init__()
#         self.params = params
#
#     def __str__(self):
#         return "[CreateExpr: params={}]".format(self.liststr(self.params))
#
#     def analyse_scope(self, scope, errorhandler):
#         for param in self.params:
#             param.analyse_scope(scope, errorhandler)
#
#     def typecheck(self, errorhandler):
#         pass
#
#     def code_gen(self):
#         pass


class UnaryExpr(Expr):
    """ p_exprUNARYEXPRESSIONS """
    def __init__(self, op, operand):
        super().__init__()
        self.op = op
        self.operand = operand

    def __str__(self):
        return "[UnaryExpr: op=" + str(self.op) + ", operand=" + str(self.operand) + "]"

    def analyse_scope(self, scope, errorhandler):
        self.operand.analyse_scope(scope, errorhandler)

    def typecheck(self, errorhandler):
        self.operand.typecheck(errorhandler)
        if self.op == '#':
            if self.operand.marm_type != 'string':
                errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                           "Operator '#' expects one argument of type string")
            self.marm_type = Typename('int')
        elif self.op == '-':
            if self.operand.marm_type != 'int':
                errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                           "Operator '-' expects one argument of type int.")
            else:
                self.marm_type = Typename('int')
        else:
            errorhandler.registerFatal(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Typechecking failed on unknown operator {}".format(self.op))

    def code_gen(self, errorhandler):
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


# class LHSExpr(Expr):
#     """ p_exprLHS """
#     def __init__(self, lhs):
#         super().__init__()
#         self.lhs = lhs

#     def __str__(self):
#         return "[LHSExpr: lhs=" + str(self.lhs) + "]"

#     def analyse_scope(self, scope, errorhandler):
#         self.lhs.analyse_scope(scope, errorhandler)

#     def typecheck(self, errorhandler):
#         self.lhs.typecheck(errorhandler)

#     def code_gen(self):
#         """Pushes the address of the identifier stored in the lhs"""
#         return self.lhs.code_gen()


class StructExpr(Expr):
    """ p_exprSTRUCTACCESS """
    def __init__(self, expr, ident):
        super().__init__()
        self.expr = expr
        self.ident = ident

    def __str__(self):
        return "[StructExpr: expr=" + str(self.expr) + ", ident=" + str(self.ident) + "]"

    def analyse_scope(self, scope, errorhandler):
        self.expr.analyse_scope(scope,errorhandler)
        # TODO: Attributes?

    def typecheck(self, errorhandler):
        self.expr.typecheck(errorhandler)
        print(self.expr)
        self.marm_type = self.expr.marm_type.attribute_type(self.ident)
        if self.marm_type is None:
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Value of type {} has not attribute named {}".format(
                                           self.expr.marm_type, self.ident))

    def code_gen(self, errorhandler):
        """TODO has not yet been decided what this should actually do"""
        code = []

        code.append("// code for struct access not implemented yet")
        return code

    def code_gen_LHS(self, errorhandler):
        """TODO do stuff"""
        code = []
        code.append("// codeLHS for struct access not implemented yet")
        code += self.expr.code_gen()
        if self.ident == "balance":
            code.append("OP_GETBAL")
        return code


class LHS(Node):
    """ Non terminal 14 """
    def __init__(self, ident):
        super().__init__()
        self.ident = ident
        self.definition = None

    def __str__(self):
        return "[LHS: ident=" + str(self.ident) + "]"

    def analyse_scope(self, scope, errorhandler):
        self.definition = scope.lookup(self.ident)
        if self.definition is None:
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Use of undeclared identifier {}.".format(self.ident))

    def typecheck(self, errorhandler):
        self.marm_type = self.definition.get_marm_type_for(self.ident)

    def code_gen(self, errorhandler):
        """Pushes the address of the identifier from the symbol table on the stack"""
        code = []
        if isinstance(self.definition, Procdecl):
            code.append(self.ident + " // function name")
        elif isinstance(self.definition, ContractMemberDecl):
            code.append('"' + self.definition.name + '" // store name')
            code.append('OP_GETSTOR')
            pass
        else:
            code.append(str(self.definition.get_local_index_for(self.ident))+" // address of local "+self.ident)
            code.append('OP_PUSHR')
        return code

    def code_gen_LHS(self, errorhandler):
        """Pushes the address of the identifier from the symbol table on the stack"""
        code = []
        if isinstance(self.definition,Procdecl):
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Tried to assign to procedure name {}".format(self.ident))
            # raise RuntimeError("Tried to assign procedure name")
        elif isinstance(self.definition, ContractMemberDecl):
            code.append('"' + self.definition.name +'" // store name')
            code.append('OP_SETSTOR')
        else:
            code.append(str(self.definition.get_local_index_for(self.ident))+ " // address of local "+self.ident)
            code.append('OP_POPR')
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
        elif type(other) is str: # replace with better mechanism
            return self.typee == other
        else:
            return False

    def code_gen(self, errorhandler):
        """Should not be used at all, fails on call"""
        raise NotImplementedError

    def typecheck(self, errorhandler): pass

    def attribute_type(self, ident, errorhandler): # TODO: Add **all+* attributes we have available
        if self.typee == 'msg':
            if ident == 'account':
                return Typename('address')
        if self.typee == 'address':
            return Typename('generic')
        return None


class Translationunit(Node):
    """ Non terminal 0 """
    def __init__(self, contractdata, procdecllist):
        super().__init__()
        self.procs = procdecllist
        self.contractdata =  contractdata

    def __str__(self):
        return "[Translationunit: contractdata = "+str(self.contractdata)+" procs=" + self.liststr(self.procs) + "]"

    def analyse_scope(self, scope=None, errorhandler=None):
        local_scope = Scope(scope)
        for proc in self.procs:
            local_scope.define(proc.name, proc)
        for contractdata_el in self.contractdata:
            contractdata_el.analyse_scope(local_scope, errorhandler)
        for proc in self.procs:
            proc.analyse_scope(local_scope, errorhandler)

    def typecheck(self, errorhandler):
        for proc in self.procs:
            proc.set_global_definition_types(errorhandler)
        for proc in self.procs:
            proc.typecheck(errorhandler)

    def code_gen(self, errorhandler):
        """Calls codegen for every procedure and stores their addresses before"""
        code = ["dispatcher: // start dispatcher", "OP_SWAP"]
        procedures = []
        i = 0
        for proc in self.procs:
            procedures.append((i, proc.name, len(proc.params)))
            i += 1
        for (i, name, le_param) in procedures:
            code.append("OP_DUP")
            code.append("\"" + str(name) + "\"")
            code.append("OP_EQU")
            code.append("disp_proc" + str(i))
            code.append("OP_JUMPC")
        code.append("disp_fail")
        code.append("OP_JUMP")
        for (i, name, le_param) in procedures:
            code.append("disp_proc" + str(i) + ":")
            code.append("OP_POPVOID")
            code.append(str(le_param))
            code.append("OP_EQU")
            code.append("OP_NOT")
            code.append("disp_fail")
            code.append("OP_JUMPC")
            code.append("0")
            code.append(str(name))
            code.append("OP_CALL")
            code.append("disp_end")
            code.append("OP_JUMP")
        code.append("disp_fail:")
        code.append("OP_KILL")
        code.append("disp_end:")
        code.append("OP_RET // end dispatcher")
        for procdecl in self.procs:
            code_proc = procdecl.code_gen()
            code += code_proc
        return code


class Paramdecl(Node):
    """ Non terminal 3 """
    def __init__(self, param_type, name):
        super().__init__()
        self.param_type = param_type
        self.name = name
        self.marm_type = self.param_type
        self.param_index = None

    def __str__(self):
        return "[Paramdecl: param_type=" + str(self.param_type) + ", name=" + str(self.name) + "]"

    def analyse_scope(self, scope, errorhandler):
        if scope.has_direct_definition(self.name):
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Multiple parameters have the name {}.".format(self.name))
        scope.define(self.name, self)

    def typecheck(self, errorhandler): pass

    def get_marm_type_for(self, ident, errorhandler):
        assert(ident == self.name)
        return self.param_type

    def get_local_index_for(self, ident, errorhandler):
        return (-1)-self.param_index

    def code_gen(self, errorhandler):
        """do nothing"""
        code = []
        return code

class ContractMemberDecl(Node):
    def __init__(self, member_type, name):
        super().__init__()
        self.member_type = member_type
        self.marm_type = member_type
        self.name = name

    def __str__(self):
        return "[ContractMemberDecl: member_type={}, name={}]".format(self.member_type, self.name)

    def analyse_scope(self, scope, errorhandler):
        if scope.has_direct_definition(self.name):
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Multiple contract members have the name {}.".format(self.name))
        scope.define(self.name, self)

    def typecheck(self, errorhandler): pass

    def get_marm_type_for(self, ident, errorhandler):
        assert(ident == self.name)
        return self.marm_type


class Proctype:
    def __init__(self, return_type, param_types):
        self.return_type = return_type
        self.param_types = param_types

    def attribute_type(self, ident):
        return None

class Procdecl(Node):
    """ Non terminal 4 """
    def __init__(self, return_type, name, params, body):
        super().__init__()
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body
        self.local_depth = None

    def __str__(self):
        return "[Procdecl: return_type=" + str(self.return_type) + ", name=" + str(self.name) + ", params=" +\
               self.liststr(self.params) + ", body=" + self.liststr(self.body) + "]"

    def analyse_scope(self, scope, errorhandler):
        local_scope = Scope(scope)
        local_scope.define("#current_function", self)
        i=0
        for param in self.params:
            param.analyse_scope(local_scope, errorhandler)
            param.param_index = i
            i+=1
        for statement in self.body:
            statement.analyse_scope(local_scope, errorhandler)
        self.local_depth = local_scope.next_var_index_delta

    def get_marm_type_for(self, ident, errorhandler):
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

    def code_gen(self, errorhandler):
        """Insert the identifiers in the symboltable(?) and generate the code for the body"""
        code = []
        code.append("%s: // start proc %s" %(self.name,self.name))
        for decl in self.body:
            code += decl.code_gen()
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
        self.init_values = [0]*len(self.decllist) # TODO

    def __str__(self):
        return "[StatementDecl: typee=" + str(self.typee) + ", decllist=" + self.liststr(self.decllist) + "]"

    def analyse_scope(self, scope, errorhandler):
        self.local_var_indices = {}
        for decl in self.decllist:
            if scope.has_direct_definition(decl):
                errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                           "Variable {} declared twice".format(decl))
            scope.define(decl, self)
            self.local_var_indices[decl] = scope.get_next_var_index()

    def get_marm_type_for(self, ident, errorhandler):
        return self.typee
    def get_local_index_for(self, ident, errorhandler):
        return 2 + self.local_var_indices[ident]

    def typecheck(self, errorhandler): pass

    def code_gen(self, errorhandler):
        """Ignore the type and call code_gen on all declarations, whatever they may do"""
        code = []
        for i in range(0, len(self.decllist)):
            if isinstance(self.decllist[i], str):
                code+=[str(self.init_values[i]) + ' // decl '+self.decllist[i]]
            else:
                code += self.decllist[i].code_gen()
        return code


class StatementReturn(Statement):
    """ p_statementRETURN """
    def __init__(self, return_value):
        super().__init__()
        self.return_value = return_value
        pass

    def __str__(self):
        return "[StatementReturn: return_value=" + str(self.return_value) + "]"

    def analyse_scope(self, scope, errorhandler):
        self.function = weakref.proxy(scope.lookup("#current_function"))
        self.return_value.analyse_scope(scope, errorhandler)

    def typecheck(self, errorhandler):
        self.return_value.typecheck(errorhandler)
        if self.return_value.marm_type != self.function.marm_type.return_type:
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Can't return value of type {} from function with return type {}".format(
                                           self.return_value.marm_type, self.function.marm_type.return_type))

    def code_gen(self, errorhandler):
        """Push the return value and do OP_RET"""
        code = self.return_value.code_gen()
        code.append("OP_RET")
        return code


class StatementWhile(Statement):
    """ p_statementLOOPS """
    
    label_id = 0
    
    def __init__(self, boolex, statement):
        super().__init__()
        self.boolex = boolex
        self.statement = statement

    def __str__(self):
        return "[StatementWhile: boolex=" + str(self.boolex) + ", statement=" + str(self.statement) + "]"

    def analyse_scope(self, scope, errorhandler):
        self.boolex.analyse_scope(scope, errorhandler)
        self.statement.analyse_scope(scope, errorhandler)

    def typecheck(self, errorhandler):
        self.boolex.typecheck(errorhandler)
        if self.boolex.marm_type != 'bool':
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Condition in while statement must be of type bool, got {}.".format(
                                           self.boolex.marm_type))
        self.statement.typecheck(errorhandler)

    def code_gen(self, errorhandler):
        """First gets the bool, then negates it and jumps to end if loop is done. If not it does the body code."""
        code = []
        StatementWhile.label_id += 1
        label_start = "__label_loop_start" + str(StatementWhile.label_id)
        label_end = "__label_loop_end" + str(StatementWhile.label_id)
        code_boolex = self.boolex.code_gen()
        code_body = self.statement.code_gen()

        # Start label
        code.append(label_start + ":")

        # Get the bool
        code += code_boolex
        code.append("OP_NOT")

        code.append(label_end)
        code.append("OP_JUMPC")

        # The loop body
        code += code_body

        code.append(label_start)
        code.append("OP_JUMP")

        code.append(label_end + ":")
        return code


class StatementIf(Statement):
    """ p_statementBRANCHING """

    loop_id = 0

    def __init__(self, boolex, statement, elseprod):
        super().__init__()
        self.boolex = boolex
        self.statement = statement
        self.elseprod = elseprod

    def __str__(self):
        return "[StatementIf: boolex={}, statement={}, elseprod={}]".format(self.boolex,self.statement,self.elseprod)

    def analyse_scope(self, scope, errorhandler):
        self.boolex.analyse_scope(scope, errorhandler)
        self.statement.analyse_scope(scope, errorhandler)
        if not (self.elseprod is None):
            self.elseprod.analyse_scope(scope, errorhandler)

    def typecheck(self, errorhandler):
        self.boolex.typecheck(errorhandler)
        if self.boolex.marm_type != 'bool':
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Condition in an if statement must be of type bool.")
        self.statement.typecheck(errorhandler)

    def code_gen(self, errorhandler):
        """First the else block because less code, jumping accordingly"""
        code = []
        StatementIf.loop_id += 1
        code_boolex = self.boolex.code_gen()
        code_true = self.statement.code_gen()

        # Label of true block
        label_true = "__label_if_true" + str(StatementIf.loop_id)
        label_end = "__label_if_end" + str(StatementIf.loop_id)

        # Get the bool
        code += code_boolex

        code.append(label_true)
        code.append("OP_JUMPC")

        if not (self.elseprod is None):
            code_false = self.elseprod.code_gen()

            # The false body
            code += code_false

        code.append(label_end)
        code.append("OP_JUMP")

        # The true body
        code.append(label_true + ":")
        code += code_true
        code.append(label_end + ":")

        return code


class StatementExpression(Statement):
    """ p_statementEXPRESSIONSTATEMENT """
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

    def __str__(self):
        return "[StatementExpression: expr={}]".format(self.expr)

    def analyse_scope(self, scope, errorhandler):
        self.expr.analyse_scope(scope, errorhandler)

    def typecheck(self, errorhandler):
        self.expr.typecheck(errorhandler)

    def code_gen(self, errorhandler):
        """Just generate the code for the expr whatever that may be"""
        code = self.expr.code_gen()
        return code


class StatementBody(Statement):
    """ p_body """
    def __init__(self, body):
        super().__init__()
        self.body = body
        self.local_depth = None

    def __str__(self):
        return "[StatementBody: body={}]".format(self.liststr(self.body))

    def analyse_scope(self, scope, errorhandler):
        local_scope = Scope(scope)
        for statement in self.body:
            statement.analyse_scope(local_scope, errorhandler)
        self.local_depth = local_scope.next_var_index_delta

    def typecheck(self, errorhandler):
        for statement in self.body:
            statement.typecheck(errorhandler)

    def code_gen(self, errorhandler):
        """Generate the code for all statements in the body"""
        code = []
        for stmnt in self.body:
            code += stmnt.code_gen()
        code+=["OP_POPVOID"]*self.local_depth # pop local variables after block
        return code


class StatementBreak(Statement):
    """ p_statementBREAK """
    def __init__(self):
        super().__init__()
        pass

    def __str__(self):
        return "[StatementBreak]"

    def analyse_scope(self, scope, errorhandler): pass

    def typecheck(self, errorhandler): pass

    def code_gen(self, errorhandler):
        """Push labelname and jump there"""
        code = ["__label_loop_end" + str(StatementWhile.label_id), "OP_JUMP"]
        return code


class StatementContinue(Statement):
    """ p_statementCONTINUE """
    def __init__(self):
        super().__init__()
        pass

    def __str__(self):
        return "[StatementContinue]"

    def analyse_scope(self, scope, errorhandler): pass

    def typecheck(self, errorhandler): pass

    def code_gen(self, errorhandler):
        """Push labelname and jump there"""
        code = ["__label_loop_start" + str(StatementWhile.label_id), "OP_JUMP"]
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

    def analyse_scope(self, scope, errorhandler):
        self.left.analyse_scope(scope, errorhandler)
        self.right.analyse_scope(scope, errorhandler)

    def typecheck(self, errorhandler):
        self.left.typecheck(errorhandler)
        self.right.typecheck(errorhandler)
        if self.left.marm_type != self.right.marm_type:
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Trying to compare values of types {} and {}.".format(
                                           self.left.marm_type, self.right.marm_type))
        if self.left.marm_type not in ['int']: #TODO
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Trying to compare two values of type {}.".format(self.left.marm_type))
        self.marm_type = Typename('bool')

    def code_gen(self, errorhandler):
        """Generate code for all types of comparison after executing both sides."""
        code = []
        code += self.left.code_gen()
        code += self.right.code_gen()
        if str(self.op) == "==":
            code.append("OP_EQU")
        elif str(self.op) == "!=":
            code.append("OP_EQU")
            code.append("OP_NOT")
        elif str(self.op) == "<=":
            code.append("OP_LE")
        elif str(self.op) == ">=":
            code.append("OP_GE")
        elif str(self.op) == "<":
            code.append("OP_LT")
        elif str(self.op) == ">":
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
        return "[BoolexBinary: op={}, left={}, right={}]".format(self.op,self.left,self.right)

    def analyse_scope(self, scope, errorhandler):
        self.left.analyse_scope(scope, errorhandler)
        self.right.analyse_scope(scope, errorhandler)

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

    def code_gen(self, errorhandler):
        """Push both sides and consume them."""
        code = []
        code += self.left.code_gen()
        code += self.right.code_gen()
        if str(self.op) == "||":
            code.append("OP_OR")
        elif str(self.op) == "&&":
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

    def analyse_scope(self, scope, errorhandler):
        self.operand.analyse_scope(scope, errorhandler)

    def typecheck(self, errorhandler):
        self.operand.typecheck(errorhandler)
        if self.operand.marm_type != 'bool':
            errorhandler.registerError(self.pos_filename, self.pos_begin_line, self.pos_begin_col,
                                       "Operand of '!' needs to be of type bool.")
        self.marm_type = Typename('bool')

    def code_gen(self, errorhandler):
        """Negate the result of the operand code."""
        code = []
        code += self.operand.code_gen()
        code.append("OP_NOTS")
        return code
