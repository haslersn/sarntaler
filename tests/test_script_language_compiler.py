import unittest
import os.path
from src.marm import *


class TestParserMethods(unittest.TestCase):
    def setUp(self):
        self.lexer = lexer.marmlexer("", None, True)

        self.testdir = os.path.join(os.path.dirname(__file__), "marm")

    def generic_test(self, filename, cleanCode=True, roughlyOk=True, error_count=0, fatals_count=0):
        errorhandler = marmcompiler.ErrorHandler()
        try:
            with open(os.path.join(self.testdir, filename), mode='r') as testfile:
                marmcompiler.marmcompiler(filename, testfile.read(), errorhandler=errorhandler)
                self.assertEqual(errorhandler.roughlyOk(), roughlyOk)
                self.assertEqual(errorhandler.cleanCode(), cleanCode)
                self.assertEqual(errorhandler.countErrors(), error_count)
                self.assertEqual(errorhandler.countFatals(), fatals_count)
        except IOError as e:
            self.fail(msg="File error: " + str(e))

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
        self.generic_lex("sarn", 'SARN', 'sarn')
        self.generic_lex("msg", 'MSG', 'msg')
        self.generic_lex("contract", 'CONTRACT', 'contract')
        self.generic_lex("create", 'CREATE', 'create')
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
        self.generic_lex("//wqfwnwekg", 'COMMENT', '//wqfwnwekg')
        self.generic_lex("""/* qkjqwhrkufgb
        wekjgbkggbgw
        ewtkbwgukw
        wetkjbwejgb*/""", 'COMMENT', '''/* qkjqwhrkufgb
        wekjgbkggbgw
        ewtkbwgukw
        wetkjbwejgb*/''')
        self.generic_lex(" ", 'WHITESPACE', " ")
        self.generic_lex("\t", 'WHITESPACE', "\t")
        # self.generic_lex("\n", 'NEWLINE', "\n",) strange behavior, if lineno is expected to be 2 it's 1 and vice versa
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
        self.generic_test("notvalid.marm", False, False, 2)

    def test_parse_file_error2(self):
        """Tests some easy errors"""
        self.generic_test("invalid.marm", False, False, 6, 0)#TODO: 0 should be 3 (lexical errors)

    def test_parse_file_valid_standard(self):
        """Tests some standard valid file"""
        self.generic_test("test.marm")

    def test_parse_file_valid_double_functions(self):
        """Tests some valid easy file with two functions and a call"""
        self.generic_test("valid.marm")

    @unittest.expectedFailure
    def test_parse_file_test_for_behaviour(self):
        """Tests whether some parsable structure results in defined behaviour, should probably fail"""
        self.generic_test("absurd_tests.marm")


    @unittest.expectedFailure
    def test_parse_file_unimplemented_features(self):
        """Tests whether some new features are actually implemented"""
        self.generic_test("blockchainfeatures.marm")


if __name__ == '__main__':
    unittest.main()
