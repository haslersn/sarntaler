# Token types
tokens = ( 'IDENT',
           'NUMBER', )

# Token definitions
t_IDENT = r'[A-Za-z][A-Za-z0-9_]*'
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignore whitespace
t_ignore = " \t"

# Track line numbers for better error messages
def t_newline(t):
    r'\n+'
    t.lexer.lineno+=len(t.value)

# Error handler
def t_error(t):
    print("Line {}: Unexpected character '{}'. Skipping.".format(t.lexer.lineno, t.value[0]))
    t.lexer.skip(1) # skip this character
    # TODO better error handling

# Generate lexer
import ply.lex as lex
lexer = lex.lex()
