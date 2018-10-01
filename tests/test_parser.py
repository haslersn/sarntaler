import unittest
from src.marm import *


class TestParserMethods(unittest.TestCase):
    def setUp(self):
        self.lexer = lexer.lexer

    def generic_lex(self, t_text, t_type, t_value, t_lineno=1, t_lexpos=0):
        try:
            self.lexer.input(t_text)
            token = self.lexer.token()
            self.assertEqual(t_type, token.type)
            self.assertEqual(t_value, token.value)
            self.assertEqual(t_lineno, token.lineno)
            self.assertEqual(t_lexpos, token.lexpos)
        except lexer.LexerError as e:
            unittest.fail(msg=t_text + " could not be lexed. " + str(e))

    def test_lex_tokens(self):
        """"Tests all known tokens, has to be updated always"""
        self.generic_lex("if", 'IF', 'if')
        self.generic_lex("while", 'WHILE', 'while')
        self.generic_lex("break", 'BREAK', 'break')
        self.generic_lex("continue", 'CONTINUE', 'continue')
        self.generic_lex("else", 'ELSE', 'else')
        self.generic_lex("return", 'RETURN', 'return')
        self.generic_lex("int", 'INT', 'int')
        self.generic_lex("address", 'ADDRESS', 'address')
        self.generic_lex("i", 'IDENT', 'i')
        self.generic_lex("{", 'BEGIN', '{')
        self.generic_lex("}", 'END', '}')
        self.generic_lex(";", 'SEMI', ';')
        self.generic_lex(",", 'COMMA', ',')
        self.generic_lex("0x0000000000000000000000000000000000000000012345678912345678901234",
                         'ADDRESSVALUE', '0x0000000000000000000000000000000000000000012345678912345678901234')
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
        self.assertFalse(lexer.tokens.__len__() == 0)

    def test_parse_file_error(self):
        """Tests some quite complicated errors"""
        errorhandler = marmcompiler.ErrorHandler()
        try:
            testfile = open("./marm/notvalid.marm", mode='r')
            marmcompiler.marmcompiler("notvalid.marm", testfile.read(), errorhandler=errorhandler)
            self.assertFalse(errorhandler.roughlyOk())
            self.assertEqual(errorhandler.countErrors(), 2)
            self.assertEqual(errorhandler.countFatals(), 0)
        except IOError as e:
            self.fail(msg="File error: " + str(e))

    def test_parse_file_error2(self):
        """Tests some easy errors"""
        errorhandler = marmcompiler.ErrorHandler()
        try:
            testfile = open("./marm/invalid.marm", mode='r')
            marmcompiler.marmcompiler("invalid.marm", testfile.read(), errorhandler=errorhandler)
            self.assertFalse(errorhandler.roughlyOk())
            self.assertEqual(errorhandler.countErrors(), 5)
           # self.assertEqual(errorhandler.countFatals(), 3) TODO lexical errors should be fatals
        except IOError as e:
            self.fail(msg="File error: " + str(e))
            
    def test_parse_file_valid_standard(self):
        """Tests some standard valid file"""
        errorhandler = marmcompiler.ErrorHandler()
        try:
            testfile = open("./marm/test.marm", mode='r')
            marmcompiler.marmcompiler("test.marm", testfile.read(), errorhandler=errorhandler)
            self.assertTrue(errorhandler.cleanCode())
        except IOError as e:
            self.fail(msg="File error: " + str(e))

    def test_parse_file_valid_double_functions(self):
        """Tests some valid easy file with two functions and a call"""
        errorhandler = marmcompiler.ErrorHandler()
        try:
            testfile = open("./marm/valid.marm", mode='r')
            marmcompiler.marmcompiler("valid.marm", testfile.read(), errorhandler=errorhandler)
            self.assertTrue(errorhandler.cleanCode())
        except IOError as e:
            self.fail(msg="File error: " + str(e))


if __name__ == '__main__':
    unittest.main()
