# Token types
tokens = ( 'IDENT',
           'NUMBER', 'COMMENT' )

def t_COMMENT(t):
    r'(\/\*([^*]|\* + [^*\/])*\*+\/)|(\/\/[^\r\n]*(\r|\n|\r\n)?)'
    pass

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
