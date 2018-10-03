import unittest
import os.path
import os
from src.marm import *
from sys import stdout


class TestParserMethods(unittest.TestCase):
    def setUp(self):
        self.lexer = lexer.marmlexer("", None, True)

        self.testdir = os.path.join(os.path.dirname(__file__), "marm")

    def generic_test(self, filename, cleanCode=True, roughlyOk=True, error_count=0, fatals_count=0, stages=None,
                     print_out=False):
        errorhandler = marmcompiler.ErrorHandler()
        try:
            with open(os.path.join(self.testdir, filename), mode='r') as testfile:
                result = marmcompiler.marmcompiler(filename, testfile.read(),
                                          errorhandler=errorhandler, stages=stages)
                self.assertEqual(errorhandler.roughlyOk(), roughlyOk)
                self.assertEqual(errorhandler.cleanCode(), cleanCode)
                self.assertEqual(errorhandler.countErrors(), error_count)
                self.assertEqual(errorhandler.countFatals(), fatals_count)
                if print_out:
                    with open(os.path.join(self.testdir, "test.labvm"), "w") as output:
                        for line in result[1]:
                            output.write(str(line))
                            output.write("\n")
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
        self.generic_lex("transfer", 'TRANSFER', 'transfer')
        self.generic_lex("new", 'NEW', 'new')
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
        self.assertTrue(lexer.tokens.__len__() == 42)

    def test_parse_file_error(self):
        """Tests some quite complicated errors"""
        self.generic_test("notvalid.marm", False, False, 2)

    def test_parse_file_error2(self):
        """Tests some easy errors"""
        self.generic_test("invalid.marm", False, False, 6, 0)#TODO: 0 should be 3 (lexical errors)

    def test_parse_file_valid_standard(self):
        """Tests some standard valid file"""
        self.generic_test("test.marm", stages=['parse', 'analyse_scope', 'typecheck', 'codegen'])

    def test_parse_file_valid_double_functions(self):
        """Tests some valid easy file with two functions and a call"""
        self.generic_test("valid.marm")

    @unittest.expectedFailure
    def test_parse_file_test_for_behaviour(self):
        """Tests whether some parsable structure results in defined behaviour, should probably fail"""
        self.generic_test("absurd_tests.marm")

    @unittest.expectedFailure
    def test_parse_file_unimplemented_features(self):
        """Tests whether some new features are actually implemented and should be have any other flaws"""
        self.generic_test("blockchainfeatures.marm")

    def test_typecheck_valid(self):
        self.generic_test("valid_types.marm")

    def test_typecheck_invalid_1(self):
        self.generic_test("invalid_types_1.marm", False, False, 3, 0)

    def test_scopes_invalid(self):
        self.generic_test("scopes_invalid.marm", False, False, 4, 0)

    def test_gcd(self):
        self.generic_test("gcd.marm")

    @unittest.skipIf(os.name == 'nt', "no crypto module on windows")
    def generic_run_test(self, filename, expected_result, fnname, params=[], stores=[]):
        from subprocess import call
        from src.blockchain.account import Account
        from tests.test_scriptinterpreter import empty_mt, example_pubkey
        from src.scriptinterpreter import ScriptInterpreter
        self.generic_test(filename, print_out=True)
        call(["rm", os.path.join(self.testdir, "o.out")])
        call(["python3", "-m", "src.labvm.scriptlinker", os.path.join(self.testdir, "test.labvm"),
              "-o", os.path.join(self.testdir, "o.out")])
        with open(os.path.join(self.testdir, "o.out")) as bytecode_file:
            bytecode = bytecode_file.read()

        acc = Account(example_pubkey, 0, bytecode, 1, stores)
        mt = empty_mt.put(acc.address, acc.hash)
        si = ScriptInterpreter(mt, params[::-1]+[fnname, len(params)+1], acc, [bytes(17)], 0)
        retval = si.execute_script()
        self.assertTrue(retval is not None)
        (ignore, retval) = retval
        self.assertEqual(expected_result, retval)

    def test_gcd_script(self):
        from math import gcd
        for (a,b) in [(12,26)]:
            self.generic_run_test("gcd.marm", gcd(a,b), "gcd", [a, b])

    def test_fibonacci_inefficient(self):
        fibs = [0,1]
        def fib(n):
            nonlocal fibs
            for i in range(len(fibs),n+1):
                fibs.append(fibs[i-1] + fibs[i-2])
            return fibs[n]
        n = 5
        self.generic_run_test("fibonacci_inefficient.marm", fib(n), "fib", [n])

    def test_ackermann(self):
        def phi(a,b,n):
            if n==0:
                return a+b
            elif b==0:
                return alpha(a,n-1)
            else:
                return phi(a, phi(a,b-1,n), n-1)
        def alpha(a, n):
            if n==0:
                return 0
            elif n==1:
                return 1
            else:
                return a
        a = 2
        b = 2
        n = 3
        eres = phi(a,b,n)
        self.generic_run_test("ackermann.marm", eres, "phi", [a,b,n])

    def test_basic_arithmetic(self):
        self.generic_run_test("basic_arithmetic.marm", 1, "test_basic_arithmetic", [])

    def test_precedence(self):
        self.generic_run_test("precedence_test.marm", 2, "precedence_test", [])

    def test_address_invalid(self):
        self.generic_test("test_address_invalid.marm", False, False, 1)

    def test_address_valid(self):
        self.generic_run_test("test_address_valid.marm", 123, "test_address", [123])

    def test_calling_convention(self):
        self.generic_run_test("test_calling_convention.marm", 123, "fn1", [2, 3])
        self.generic_run_test("test_calling_convention.marm", 256, "fn2", [5, 6])
        self.generic_run_test("test_calling_convention.marm", 357, "fn3", [5, 7])

    def test_contract_global_invalid(self):
        self.generic_test("test_contract_global_invalid.marm", False, False, 1)

    def test_contract_global_valid(self):
        from src.blockchain.account import StorageItem
        stores = [StorageItem("myint", 'int', 0),
                  StorageItem("mysarn", 'int', 0)]
        self.generic_run_test("test_contract_global_valid.marm", 1234, "setmysarn", [1234], stores)
        self.generic_run_test("test_contract_global_valid.marm", -1085, "setmyint", [-1085], stores)

    def test_loop(self):
        self.generic_run_test("test_loop.marm", 1, "collatz_step", [2352, 11]) # TODO: 2nd param

    def test_new(self):
        self.generic_run_test("test_new.marm", 1, "copy_out", 21)

    def test_sarn_ok(self):
        self.generic_run_test("test_sarn_ok.marm", 12, "test_sarn", [11])

    @unittest.skipIf(True, "DOS test, takes approximately 10m, do not test if you don't want this")
    def test_DOS(self):
        self.generic_test("chaos.marm")
        # self.generic_run_test("chaos.marm", 2, "test", [0])


if __name__ == '__main__':
    unittest.main()
