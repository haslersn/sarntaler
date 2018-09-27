import unittest
import src.marm.lexer as lex


class TestParserMethods(unittest.TestCase):
    def setUp(self):
        self.lexer = lex.lexer

    def test_parse(self):
        self.lexer.input("int i;")
        token = self.lexer.token()
        print("Testtoken")
        print(str(token))


    def test_tokens_not_empty(self):
        self.assertFalse(lex.tokens.__len__() == 0)


if __name__ == '__main__':
    unittest.main()
