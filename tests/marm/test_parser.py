import unittest
import src.marm.lexer as lexer_source


class TestParserMethods(unittest.TestCase):
    def setUp(self):
        self.lexer = lexer_source.lexer

    def generic_parse(self, t_text, t_type, t_value, t_lineno=1, t_lexpos=0):
        self.lexer.input(t_text)
        token = self.lexer.token()
        self.assertEqual(t_type, token.type)
        self.assertEqual(t_value, token.value)
        self.assertEqual(t_lineno, token.lineno)
        self.assertEqual(t_lexpos, token.lexpos)

    def test_parse(self):
        self.generic_parse("if", 'IF', 'if')
        self.generic_parse("while", 'WHILE', 'while')
        self.generic_parse("break", 'BREAK', 'break')
        self.generic_parse("continue", 'CONTINUE', 'continue')
        self.generic_parse("else", 'ELSE', 'else')
        self.generic_parse("return", 'RETURN', 'return')
        self.generic_parse("int", 'INT', 'int')
        self.generic_parse("i", 'IDENT', 'i')
        self.generic_parse("{", 'BEGIN', '{')
        self.generic_parse("}", 'END', '}')
        self.generic_parse(";", 'SEMI', ';')
        self.generic_parse(",", 'COMMA', ',')
        self.generic_parse("0x0000000000000000000000000000000000000000012345678912345678901234"
                           , 'ADDRESS', '0x0000000000000000000000000000000000000000012345678912345678901234')
        self.generic_parse("0x4", 'ADDRESS', '0x4')
        self.generic_parse("=", 'ASSIGN', '=')
        self.generic_parse("23", 'INTCONST', 23)
        self.generic_parse("+", 'ADDOP', '+')
        self.generic_parse("-", 'SUBOP', '-')
        self.generic_parse("*", 'MULOP', '*')
        self.generic_parse("/", 'DIVOP', '/')
        self.generic_parse("#", 'HASH', '#')
        self.generic_parse(".", 'DOT', '.')
        self.generic_parse("!", 'NOT', '!')
        self.generic_parse("==", 'EQ', '==')
        self.generic_parse("&&", 'AND', '&&')
        self.generic_parse("||", 'OR', '||')
        self.generic_parse("!=", 'NEQ', '!=')
        self.generic_parse(">", 'GT', '>')
        self.generic_parse("<", 'LT', '<')
        self.generic_parse(">=", 'GEQ', '>=')
        self.generic_parse("<=", 'LEQ', '<=')
        self.generic_parse("(", 'LPAR', '(')
        self.generic_parse(")", 'RPAR', ')')


    def test_tokens_not_empty(self):
        self.assertFalse(lexer_source.tokens.__len__() == 0)


if __name__ == '__main__':
    unittest.main()
