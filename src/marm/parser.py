
start = 'translationunit'

from lexer import tokens

def p_translationunit(p):
    'translationunit : procdecl'

def p_procdecl(p):
    'procdecl : type IDENT LPAR paramlist RPAR statementlistOPT'

def p_statementlistOPT(p):
    '''statementlistOPT : BEGIN statementlist END
                        | SEMI '''

def p_statementlist(p):
    '''statementlist : statement statementlist
                       | '''
def p_paramlist(p):
    '''paramlist : paramdecl COMMA paramlist 
                 | paramdecl '''
                 
def p_paramdecl(p):
    'paramdecl : type IDENT'

def p_type(p):
    'type : typename'

def p_typename(p):
    '''typename : ADDRESS 
    | INT'''

def p_statement(p):
    'statement : RETURN SEMI'

def p_error(p):
    print("Syntax error at ('%s')" % p.error)

# Generate parser
import ply.yacc as yacc
yacc = yacc.yacc()

# Main for Debugging/Testing
if __name__=="__main__":
    # Parse Arguments
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Parse the given file')
    parser.add_argument('--input', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()

    #TODO: actual parser test
    from lexer import lexer
    result = yacc.parse(args.input.read(), lexer=lexer)
    args.output.write(result)
