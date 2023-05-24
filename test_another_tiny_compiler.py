import unittest

from another_tiny_compiler import tokenize, parse


class TestParse(unittest.TestCase):
    def test_empty_code(self):
        program_text = ""

        token_seq = tokenize(program_text)
        with self.assertRaises(IndexError):
            ast, _ = parse(token_seq)

    def test_single_literal(self):
        program_text = "1"

        token_seq = tokenize(program_text)
        ast, _ = parse(token_seq)
        # print(ast)

        self.assertEqual(ast, {'type': 'NumberLiteral', 'value': '1'})

    def test_single_call(self):
        program_text = "(print 1)"

        token_seq = tokenize(program_text)
        ast, _ = parse(token_seq)
        # print(ast)

        self.assertEqual(ast, {
            'type': 'CallExpression',
            'name': 'print',
            'params': [
                {'type': 'NumberLiteral', 'value': '1'},
            ],
        })

    def test_nested_calls(self):
        program_text = "(print (add 1 2) (subtract 3 4))"

        token_seq = tokenize(program_text)
        ast, _ = parse(token_seq)
        # print(ast)

        self.assertEqual(ast, {
            'type': 'CallExpression',
            'name': 'print',
            'params': [
                {
                    'type': 'CallExpression',
                    'name': 'add', 'params': [
                        {
                            'type': 'NumberLiteral',
                            'value': '1'
                        },
                        {
                            'type': 'NumberLiteral',
                            'value': '2'
                        },
                    ],
                },
                {
                    'type': 'CallExpression',
                    'name': 'subtract',
                    'params': [
                        {
                            'type': 'NumberLiteral',
                            'value': '3'
                        },
                        {
                            'type': 'NumberLiteral',
                            'value': '4'
                        },
                    ],
                },
            ],
        })

    def test_missing_closing_paren(self):
        program_text = "(print 1"

        token_seq = tokenize(program_text)
        with self.assertRaises(IndexError):
            ast, _ = parse(token_seq)


if __name__ == '__main__':
    unittest.main()
