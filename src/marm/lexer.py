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

# Helper function to calculate the current column number
def column_number(token):
    line_start = token.lexer.lexdata.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

# Error handler
def t_error(t):
    print("Line {}, Column {}: Unexpected character '{}'. Skipping."
          .format(t.lexer.lineno,
                  column_number(t),
                  t.value[0]))
    t.lexer.skip(1) # skip this character
    # TODO better error handling

# Generate lexer
import ply.lex as lex
lexer = lex.lex()
