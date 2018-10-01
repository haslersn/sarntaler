# Hash map for reserved keywords
keywords = {
    'if': 'IF',
    'while': 'WHILE',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'else': 'ELSE',
    'return': 'RETURN',
    'int': 'INT',
    'address': 'ADDRESS',
    'sarn':'SARN',
    'msg':'MSG',
    'contract':'CONTRACT'
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
          'ADDRESSVALUE',
          'ASSIGN',
          'INTCONST',
          'COMMENT',
          'WHITESPACE',
          'NEWLINE',
          'ADDOP', 'SUBOP', 'MULOP', 'DIVOP',
          'HASH', 'DOT', 'NOT', 'EQ', 'AND', 'OR', 'NEQ', 'GT', 'LT', 'GEQ', 'LEQ',
          'LPAR', 'RPAR'] + list(keywords.values())


def t_COMMENT(t):
    r'(\/\*([^*]|\* + [^*\/])*\*+\/)|(\/\/[^\r\n]*)'
    #r'(\/\*([^*]|\* + [^*\/])*\*+\/)|(\/\/[^\r\n]*(\r|\n|\r\n)?)'
    if t.lexer.returnWhitespaces:
        return t
    else:
        pass


# Token definitions
def t_IDENT(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = keywords.get(t.value, 'IDENT')
    return t


# TODO: ADDRESS SHOULD INCLUDE VALID DEFINITION OF SUCH
#       AS OF NOW AN ADDRESS IS ANY HEX NUMBER WITH MAX.
#       64 DIGITS AND MIN. 1 DIGIT
def t_ADDRESSVALUE(t):
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
#t_ignore = " \t"
def t_whitespace(t):
    r'[ \t]'
    if t.lexer.returnWhitespaces:
        t.type = keywords.get(t.value, 'WHITESPACE')
        return t
    else:
        pass


# Track line numbers for better error messages
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    if t.lexer.returnWhitespaces:
        t.type = keywords.get(t.value, 'NEWLINE')
        return t
    else:
        pass


# Helper function to calculate the current column number
def column_number_from_lexpos(input, lexpos):
    line_start = input.rfind('\n', 0, lexpos) + 1
    return (lexpos - line_start) + 1
def column_number(token):
    return column_number_from_lexpos(token.lexer.lexdata, token.lexpos)


# Error handling
## class for lexer errors
class LexerError(RuntimeError):
    def __init__(self, token):
        self.line = token.lexer.lineno
        self.column = column_number(token)
        self.error_token = token
        # Useful error message
        super().__init__("{}:{}.{}: lexical error: Invalid character '{}'."
                         .format(lexer.filename,
                                 self.line,
                                 self.column,
                                 self.error_token.value[0]))


## error handler
def t_error(t):
    #raise LexerError(t)
    t.lexer.errorhandler.registerError(
            t.lexer.filename,
            t.lexer.lineno,
            column_number(t),
            "lexical error: invalid character {}".format(t.value[0])
            )

    t.lexer.skip(1)

# Generate lexer
import ply.lex as lex

def marmlexer(filename,errorhandler,returnWhitespaces=False):
    locallexer = lex.lex()
    locallexer.filename = filename
    locallexer.errorhandler = errorhandler
    locallexer.returnWhitespaces=returnWhitespaces
    return locallexer


lexer = lex.lex()
# Main for Debugging/Testing
if __name__ == "__main__":
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
