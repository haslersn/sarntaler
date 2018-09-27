
precedence=(
     ('right','ASSIGN'),
     ('right','HASH','NOT'),
     ('right','ELSE', 'AND', 'OR', 'ADDOP', 'DIVOP', 'MULOP', 'SUBOP'),
     ('right','IF_WITHOUT_ELSE'),
)

start = 'translationunit'

from lexer import tokens

def p_translationunit(p):
    'translationunit : procdecl'


def p_procdecl(p):
    'procdecl : type IDENT LPAR paramlistopt RPAR statementlistOPT'


def p_statementlistOPT(p):
    'statementlistOPT : body'
    p[0] = p[1]
def p_statementlistOPT(p):
    'statementlistOPT : SEMI'
    p[0] = None


def p_statementlist(p):
    '''statementlist : statement statementlist
                       | '''
    if len(p)==1:
        p[0] = []
    else:
        p[2].insert(0, p[1])
        p[0] = p[2]


def p_body(p):
    'body : BEGIN statementlist END '


def p_paramlistopt(p):
    '''paramlistopt : paramlist 
                    |  '''
    if len(p)==1:
        p[0] = []
    else:
        p[0] = p[1]


def p_paramlist(p):
    '''paramlist : paramdecl COMMA paramlist
                 | paramdecl '''
    if len(p)==2:
        p[0] = [p[1]]
    else:
        p[2].insert(0,p[1])
        p[0] = p[2]


def p_paramdecl(p):
    'paramdecl : type IDENT'


def p_type(p):
    'type : typename'


def p_typename(p):
    '''typename : ADDRESS
    | INT'''


def p_statementRETURN(p):
    'statement : RETURN expr SEMI'


def p_statementLOOPS(p):
    '''statement : WHILE LPAR boolex RPAR statement '''


def p_elseprod(p):
    '''elseprod : ELSE statement %prec ELSE
    | %prec IF_WITHOUT_ELSE '''


def p_statementBRANCHING(p):
    '''statement : IF LPAR boolex RPAR statement elseprod '''


def p_statementEXPRESSIONSTATEMENT(p):
    'statement : expr SEMI'


def p_statementNEWSCOPE(p):
    'statement : body'


def p_statementLOOPkeywords(p):
    '''statement : BREAK SEMI
                 | CONTINUE  SEMI '''


def p_statementDECL(p):
    'statement : type decllist SEMI'


def p_expr(p):
    'expr : INTCONST'


def p_exprBINARYEXPRESSIONS(p):
     '''expr : expr ASSIGN expr
             | expr MULOP expr
             | expr ADDOP expr
             | expr DIVOP expr
             | expr SUBOP expr '''


def p_exprUNARYEXPRESSIONS(p):
    '''expr : HASH expr
            | SUBOP expr '''


def p_exprLHS(p):
    'expr : lhsexpression'


def p_exprNESTED(p):
    'expr : LPAR expr RPAR'
    p[0] = p[2]


def p_exprSTRUCTACCESS(p):
    'expr : expr DOT IDENT'


def p_lhsexpression(p):
    'lhsexpression : IDENT'


def p_boolexCOMPARE(p):
    '''boolex : expr EQ expr
              | expr NEQ expr
              | expr LEQ expr
              | expr GEQ expr
              | expr LT expr
              | expr GT expr'''


def p_boolexBINARY(p):
    '''boolex : boolex OR boolex
              | boolex AND boolex'''


def p_boolexUNARY(p):
    'boolex : NOT boolex'


def p_boolexPAR(p):
    'boolex : LPAR boolex RPAR'


def p_declarator(p):
    'decl : IDENT'


def p_declaratorlist(p):
    ''' decllist : decl COMMA decllist
                 | decl '''
    if len(p)==2:
        p[0] = [p[1]]
    else:
        p[3].insert(0,p[1])
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
        from lexer import column_number
        super().__init__("Unexpected token '{}' ({}) at Line {}, Column {}"
                         .format(got.value, got.type,
                                 got.lineno, column_number(got)))
def p_error(t):
    if t is None:
        raise EofError()
    else:
        raise UnexpectedTokenError(t)

# Generate parser
import ply.yacc as yacc
yacc = yacc.yacc()

# Main for Debugging/Testing
if __name__=="__main__":
    # Parse Arguments
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Parse the given file')
    parser.add_argument('--input', type=argparse.FileType('r'), default=sys.stdin,
                        help="Input file. Defaults to stdin")
    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout,
                        help="Output file. Defaults to stdout")
    args = parser.parse_args()

    #TODO: actual parser test
    from lexer import lexer
    result = yacc.parse(args.input.read(), lexer=lexer)
    args.output.write(str(result))
