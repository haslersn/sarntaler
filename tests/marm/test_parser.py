import unittest
import src.marm.lexer as lexer_source
from src.marm.parser import marmparser, ParserError


class TestParserMethods(unittest.TestCase):
    def setUp(self):
        self.lexer = lexer_source.lexer

    def generic_lex(self, t_text, t_type, t_value, t_lineno=1, t_lexpos=0):
        try:
            self.lexer.input(t_text)
            token = self.lexer.token()
            self.assertEqual(t_type, token.type)
            self.assertEqual(t_value, token.value)
            self.assertEqual(t_lineno, token.lineno)
            self.assertEqual(t_lexpos, token.lexpos)
        except lexer_source.LexerError as e:
            unittest.fail(msg=t_text + " could not be lexed. " + str(e))

    def test_lex_tokens(self):
        self.generic_lex("if", 'IF', 'if')
        self.generic_lex("while", 'WHILE', 'while')
        self.generic_lex("break", 'BREAK', 'break')
        self.generic_lex("continue", 'CONTINUE', 'continue')
        self.generic_lex("else", 'ELSE', 'else')
        self.generic_lex("return", 'RETURN', 'return')
        self.generic_lex("int", 'INT', 'int')
        self.generic_lex("i", 'IDENT', 'i')
        self.generic_lex("{", 'BEGIN', '{')
        self.generic_lex("}", 'END', '}')
        self.generic_lex(";", 'SEMI', ';')
        self.generic_lex(",", 'COMMA', ',')
        self.generic_lex("0x0000000000000000000000000000000000000000012345678912345678901234"
                         , 'ADDRESSVALUE', '0x0000000000000000000000000000000000000000012345678912345678901234')
        self.generic_lex("0x4", 'ADDRESSVALUE', '0x4')
        self.generic_lex("=", 'ASSIGN', '=')
        self.generic_lex("23", 'INTCONST', 23)
        self.generic_lex("+", 'ADDOP', '+')
        self.generic_lex("-", 'SUBOP', '-')
        self.generic_lex("*", 'MULOP', '*')
        self.generic_lex("/", 'DIVOP', '/')
        self.generic_lex("#", 'HASH', '#')
        self.generic_lex(".", 'DOT', '.')
        self.generic_lex("!", 'NOT', '!')
        self.generic_lex("==", 'EQ', '==')
        self.generic_lex("&&", 'AND', '&&')
        self.generic_lex("||", 'OR', '||')
        self.generic_lex("!=", 'NEQ', '!=')
        self.generic_lex(">", 'GT', '>')
        self.generic_lex("<", 'LT', '<')
        self.generic_lex(">=", 'GEQ', '>=')
        self.generic_lex("<=", 'LEQ', '<=')
        self.generic_lex("(", 'LPAR', '(')
        self.generic_lex(")", 'RPAR', ')')

    def test_tokens_not_empty(self):
        self.assertFalse(lexer_source.tokens.__len__() == 0)

    def test_parse_file(self):
        try:
            marmparser("test.marm")
        except ParserError:
            unittest.fail(msg="Couldn't parse file.")


if __name__ == '__main__':
    unittest.main()
