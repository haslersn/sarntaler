import unittest
import src.marm.lexer as lexer


class TestParserMethods(unittest.TestCase):
    def setUp(self):
        self.lexer = lexer.lexer

    def generic_parse(self, t_text, t_type, t_value, t_lineno, t_lexpos):
        self.lexer.input(t_text)
        token = self.lexer.token()
        self.assertEqual(token.type, t_type)
        self.assertEqual(token.value, t_value)
        self.assertEqual(token.lineno, t_lineno)
        self.assertEqual(token.lexpos, t_lexpos)

    def test_parse(self):
        self.generic_parse("int", 'INT', 'int', 1, 0)

    def test_tokens_not_empty(self):
        self.assertFalse(lexer.tokens.__len__() == 0)


if __name__ == '__main__':
    unittest.main()
