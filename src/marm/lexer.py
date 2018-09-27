# Hash map for reserved keywords
keywords = {
    'if' : 'IF',
    'while' : 'WHILE',
    'break' : 'BREAK',
    'continue' : 'CONTINUE',
    'else' : 'ELSE',
    'return' : 'RETURN',
    'int' : 'INT',
    #   'void' : 'VOID',
    #   'goto' : 'GOTO',
    #   'default' : 'DEFAULT',
    #   'for' : 'FOR',
    #   'do' : 'DO',
}

# Token types
tokens = ['IDENT',
           'BEGIN',
           'END',
           'SEMI',
           'COMMA',
           'ADDRESS',
           'ASSIGN',
           'INTCONST',
           'ADDOP', 'SUBOP', 'MULOP', 'DIVOP',
           'HASH', 'DOT', 'NOT', 'EQ', 'AND', 'OR', 'NEQ', 'GT', 'LT', 'GEQ', 'LEQ',
           'LPAR', 'RPAR'] + list(keywords.values())


def t_COMMENT(t):
    r'(\/\*([^*]|\* + [^*\/])*\*+\/)|(\/\/[^\r\n]*(\r|\n|\r\n)?)'
    pass


# Token definitions
def t_IDENT(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = keywords.get(t.value, 'IDENT')
    return t


# TODO: ADDRESS SHOULD INCLUDE VALID DEFINITION OF SUCH
#       AS OF NOW AN ADDRESS IS ANY HEX NUMBER WITH MAX.
#       64 DIGITS AND MIN. 1 DIGIT
def t_ADDRESS(t):
    r'0x\d{1,64}'
    return t


def t_INTCONST(t):
    r'\d+'
    t.value = int(t.value)
    return t



# HASH
def t_HASH(t):
    r'\#'
    return t


# DOT, COMMA, SEMI
def t_DOT(t):
    r'\.'
    return t


def t_COMMA(t):
    r','
    return t


def t_SEMI(t):
    r';'
    return t


# BEGIN and END
def t_BEGIN(t):
    r'\{'
    return t


def t_END(t):
    r'\}'
    return t

# Assign
t_ASSIGN = r'='

# Numeric operations
t_ADDOP = r'\+'
t_SUBOP = r'-'
t_MULOP = r'\*'
t_DIVOP = r'/'

# Bool operations
t_OR = r'\|\|'
t_AND = r'&&'
t_EQ = r'=='
t_NEQ = r'!='
t_GT = r'>'
t_LT = r'<'
t_GEQ = r'>='
t_LEQ = r'<='
t_NOT = r'!'

# Parentheses
t_LPAR = r'\('
t_RPAR = r'\)'

# Ignore whitespace
t_ignore = " \t"

# Track line numbers for better error messages
def t_newline(t):
    r'\n+'
    t.lexer.lineno+=len(t.value)

# Helper function to calculate the current column number
def column_number(token):
    line_start = token.lexer.lexdata.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

# Error handling
## class for lexer errors
class LexerError(RuntimeError):
    def __init__(self, token):
        self.line = token.lexer.lineno
        self.column = column_number(token)
        self.error_token = token
        # Useful error message
        super().__init__("Line {}, Column {}: Invalid character '{}'."
                         .format(self.line,
                                 self.column,
                                 self.error_token.value[0]))

## error handler
def t_error(t):
    raise LexerError(t)

# Generate lexer
import ply.lex as lex
lexer = lex.lex()

# Main for Debugging/Testing
if __name__=="__main__":
    # Parse Arguments
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Lex the given file')
    parser.add_argument('--input', type=argparse.FileType('r'), default=sys.stdin,
                        help='the input file. defaults to stdin')
    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout,
                        help='the output file. defaults to stdout')
    args = parser.parse_args()

    # Read input into string and initialize lexer
    lexer.input(args.input.read())

    # Lex input and wrtie to output
    token = lexer.token()
    while not (token is None):
        args.output.write(str(token))
        args.output.write("\n")
        token = lexer.token()
