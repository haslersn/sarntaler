from src.marm import ast as ast
import ply.yacc as yacc

precedence = (
     ('right', 'ASSIGN'),
     ('right', 'HASH', 'NOT'),
     ('right', 'ELSE', 'AND', 'OR', 'ADDOP', 'DIVOP', 'MULOP', 'SUBOP'),
     ('right', 'IF_WITHOUT_ELSE'),
)


start = 'translationunit'


def p_translationunit(p):
    'translationunit : procdecl'
    p[0] = ast.Translationunit(p[1])


def p_procdecl(p):
    'procdecl : type IDENT LPAR paramlistopt RPAR statementlistOPT'
    p[0] = ast.Procdecl(p[1], p[2], p[4], p[6])

def p_procdeclERROR(p):
    '''procdecl : error END
                | LPAR paramlistopt RPAR statementlistOPT
                | error statementlistOPT'''


def p_statementlistOPT_body(p):
    'statementlistOPT : body'
    p[0] = p[1]


def p_statementlistOPT_empty(p):
    'statementlistOPT : SEMI'
    p[0] = []


def p_statementlist(p):
    '''statementlist : statement statementlist
                       | '''
    if len(p) == 1:
        p[0] = []
    else:
        p[2].insert(0, p[1])
        p[0] = p[2]


def p_body(p):
    'body : BEGIN statementlist END '
    p[0] = p[2]


def p_paramlistopt(p):
    '''paramlistopt : paramlist 
                    |  '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]


def p_paramlist(p):
    '''paramlist : paramdecl COMMA paramlist
                 | paramdecl '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[2].insert(0,p[1])
        p[0] = p[2]


def p_paramdecl(p):
    'paramdecl : type IDENT'
    p[0] = ast.Paramdecl(p[1], p[2])


def p_type(p):
    'type : typename'
    p[0] = p[1]


def p_typename(p):
    '''typename : ADDRESS
    | INT'''
    p[0] = ast.Typename(p[1])


def p_statementRETURN(p):
    'statement : RETURN expr SEMI'
    p[0] = ast.StatementReturn(p[2])


def p_statementLOOPS(p):
    '''statement : WHILE LPAR boolex RPAR statement '''
    p[0] = ast.StatementWhile(p[3], p[5])


def p_elseprod(p):
    '''elseprod : ELSE statement %prec ELSE
    | %prec IF_WITHOUT_ELSE '''
    if len(p) == 1:
        p[0] = None
    else:
        p[0] = p[2]


def p_statementBRANCHING(p):
    '''statement : IF LPAR boolex RPAR statement elseprod '''
    p[0] = ast.StatementIf(p[3], p[5], p[6])


def p_statementEXPRESSIONSTATEMENT(p):
    'statement : expr SEMI'
    p[0] = ast.StatementExpression(p[1])


def p_statementNEWSCOPE(p):
    'statement : body'
    p[0] = ast.StatementBody(p[1])


def p_statementBREAK(p):
    'statement : BREAK SEMI'
    p[0] = ast.StatementBreak()


def P_statementCONTINUE(p):
    'statement: CONTINUE SEMI'
    p[0] = ast.StatementContinue()


def p_statementDECL(p):
    'statement : type decllist SEMI'
    p[0] = ast.StatementDecl(p[1], p[2])

def p_statementERROR(p):
    'statement : error SEMI'


def p_expr(p):
    'expr : INTCONST'
    p[0] = ast.ConstExpr(p[1])


def p_exprBINARYEXPRESSIONS(p):
     '''expr : expr ASSIGN expr
             | expr MULOP expr
             | expr ADDOP expr
             | expr DIVOP expr
             | expr SUBOP expr '''
     p[0] = ast.BinExpr(p[2], p[1], p[3])


def p_exprUNARYEXPRESSIONS(p):
    '''expr : HASH expr
            | SUBOP expr '''
    p[0] = ast.UnaryExpr(p[1], p[2])


def p_exprLHS(p):
    'expr : lhsexpression'
    p[0] = p[1]


def p_exprNESTED(p):
    'expr : LPAR expr RPAR'
    p[0] = p[2]


def p_exprSTRUCTACCESS(p):
    'expr : expr DOT IDENT'
    p[0] = ast.StructExpr(p[1], p[3])


def p_lhsexpression(p):
    'lhsexpression : IDENT'
    p[0] = ast.LHS(p[1])


def p_boolexCOMPARE(p):
    '''boolex : expr EQ expr
              | expr NEQ expr
              | expr LEQ expr
              | expr GEQ expr
              | expr LT expr
              | expr GT expr'''
    p[0] = ast.BoolexCMP(p[2], p[1], p[3])


def p_boolexBINARY(p):
    '''boolex : boolex OR boolex
              | boolex AND boolex'''
    p[0] = ast.BoolexBinary(p[2], p[1], p[3])


def p_boolexUNARY(p):
    'boolex : NOT boolex'
    p[0] = ast.BoolexNot(p[1], p[2])


def p_boolexPAR(p):
    'boolex : LPAR boolex RPAR'
    p[0] = p[2]


def p_declarator(p):
    'decl : IDENT'
    p[0] = p[1]


def p_declaratorlist(p):
    ''' decllist : decl COMMA decllist
                 | decl '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[3].insert(0, p[1])
        p[0] = p[3]


# Error handling
class ParserError(RuntimeError):
    def __init__(self, msg):
        super().__init__(msg)


class EofError(ParserError):
    def __init__(self):
        super().__init__("Unexpected end of file.")


class UnexpectedTokenError(ParserError):
    def __init__(self, got):
        from src.marm.lexer import column_number
        super().__init__("{}:{}.{}: syntax error: unexpected token {}"
                                        .format(yacc.filename,got.lexer.lineno+1,column_number(got),got))


def p_error(t):
    from src.marm.lexer import column_number
    if t is None:
        raise EofError()
    else:
        from src.marm.lexer import column_number
        yacc.errorhandler.registerError(yacc.filename,
            t.lexer.lineno,
            column_number(t),
            ("syntax error: unexpected token %s:%s" % (t.type,t.value))
            )
            

from src.marm.lexer import lexer, tokens
# Generate parser
yacc = yacc.yacc()

def marmparser(filename,input,errorhandler):
    lexer.filename=filename
    lexer.errorhandler=errorhandler
    yacc.filename=filename
    yacc.errorhandler=errorhandler
    return yacc.parse(input,lexer=lexer)

# Main for Debugging/Testing
if __name__ == "__main__":
    # Parse Arguments
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Parse the given file')
    parser.add_argument('--input', type=argparse.FileType('r'), default=sys.stdin,
                        help="Input file. Defaults to stdin")
    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout,
                        help="Output file. Defaults to stdout")
    parser.add_argument('--output-format', choices=['json', 'str'], default='json',
                        help="Format used for output. Defaults to json")
    args = parser.parse_args()
    try:
        result = marmparser(args.input.name,args.input.read())
    except ParserError as err:
        print(err)
    else:
        if result is not None:
            if args.output_format == 'json':
                args.output.write(result.toJSON())
            elif args.output_format == 'str':
                args.output.write(str(result))
            else:
                print("Unknown output format {}.".format(args.output_format))
