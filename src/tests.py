import unittest
from lexer import parse
from builder import build
from interpreter import execute
from tok import Token, TokenType
from compiler import compile2bytes
from machine import run
import node

class LexerTest(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(parse('1'), [Token('1', TokenType.INTEGER)])
        self.assertEqual(parse('234'), [Token('234', TokenType.INTEGER)])
        self.assertEqual(parse('1 23 456'), [
            Token('1', TokenType.INTEGER),
            Token('23', TokenType.INTEGER),
            Token('456', TokenType.INTEGER),
        ])

    def test_real(self):
        self.assertEqual(parse('1.1'), [Token('1.1', TokenType.REAL)])
        self.assertEqual(parse('03.1415'), [Token('03.1415', TokenType.REAL)])
        self.assertEqual(parse('1.1 2.2 3.3'), [
            Token('1.1', TokenType.REAL),
            Token('2.2', TokenType.REAL),
            Token('3.3', TokenType.REAL),
        ])

    def test_operator(self):
        self.assertEqual(parse('+'), [Token('+', TokenType.OPERATOR)])
        self.assertEqual(parse('-'), [Token('-', TokenType.OPERATOR)])
        self.assertEqual(parse('+ - + -'), [
            Token('+', TokenType.OPERATOR),
            Token('-', TokenType.OPERATOR),
            Token('+', TokenType.OPERATOR),
            Token('-', TokenType.OPERATOR),
        ])

    def test_numeric_expression(self):
        self.assertEqual(parse('1+1'), [
            Token('1', TokenType.INTEGER),
            Token('+', TokenType.OPERATOR),
            Token('1', TokenType.INTEGER),
        ])
        self.assertEqual(parse('+-3.14 + 1'), [
            Token('+', TokenType.OPERATOR),
            Token('-', TokenType.OPERATOR),
            Token('3.14', TokenType.REAL),
            Token('+', TokenType.OPERATOR),
            Token('1', TokenType.INTEGER),
        ])
        self.assertEqual(parse('1+++--2.2---+1'), [
            Token('1', TokenType.INTEGER),
            Token('+', TokenType.OPERATOR),
            Token('+', TokenType.OPERATOR),
            Token('+', TokenType.OPERATOR),
            Token('-', TokenType.OPERATOR),
            Token('-', TokenType.OPERATOR),
            Token('2.2', TokenType.REAL),
            Token('-', TokenType.OPERATOR),
            Token('-', TokenType.OPERATOR),
            Token('-', TokenType.OPERATOR),
            Token('+', TokenType.OPERATOR),
            Token('1', TokenType.INTEGER),
        ])
        self.assertEqual(parse('10**2'), [
            Token('10', TokenType.INTEGER),
            Token('**', TokenType.OPERATOR),
            Token('2', TokenType.INTEGER)
        ])
        self.assertEqual(parse('2*10**2*2'), [
            Token('2', TokenType.INTEGER),
            Token('*', TokenType.OPERATOR),
            Token('10', TokenType.INTEGER),
            Token('**', TokenType.OPERATOR),
            Token('2', TokenType.INTEGER),
            Token('*', TokenType.OPERATOR),
            Token('2', TokenType.INTEGER)
        ])

    def test_paren(self):
        self.assertEqual(parse('2*((1+3)/2+1)'), [
            Token('2', TokenType.INTEGER),
            Token('*', TokenType.OPERATOR),
            Token('(', TokenType.PAREN),
            Token('(', TokenType.PAREN),
            Token('1', TokenType.INTEGER),
            Token('+', TokenType.OPERATOR),
            Token('3', TokenType.INTEGER),
            Token(')', TokenType.PAREN),
            Token('/', TokenType.OPERATOR),
            Token('2', TokenType.INTEGER),
            Token('+', TokenType.OPERATOR),
            Token('1', TokenType.INTEGER),
            Token(')', TokenType.PAREN),
        ])

class BuilderTest(unittest.TestCase):
    def test_literal(self):
        self.assertEqual(build('1'), node.ProgramNode(subs=[
            node.ValueNode(Token('1', TokenType.INTEGER))
        ]))
        self.assertEqual(build('3.1415'), node.ProgramNode(subs=[
            node.ValueNode(Token('3.1415', TokenType.REAL))
        ]))

    def test_factor(self):
        self.assertEqual(build('-1'), node.ProgramNode(subs=[
            node.TermNode(Token('-', TokenType.OPERATOR), [
                node.ValueNode(Token('1', TokenType.INTEGER))
            ])
        ]))

    def test_numeric_expression(self):
        self.assertEqual(build('1+2'), node.ProgramNode(subs=[
            node.OpNode(Token('+', TokenType.OPERATOR), [
                node.ValueNode(Token('1', TokenType.INTEGER)),
                node.ValueNode(Token('2', TokenType.INTEGER))
            ])
        ]))
        self.assertEqual(build('-1+2'), node.ProgramNode(subs=[
            node.OpNode(Token('+', TokenType.OPERATOR), [
                node.TermNode(Token('-', TokenType.OPERATOR), [
                    node.ValueNode(Token('1', TokenType.INTEGER))
                ]),
                node.ValueNode(Token('2', TokenType.INTEGER))
            ])
        ]))
        self.assertEqual(build('+-3.14 + 1'), node.ProgramNode(subs=[
            node.OpNode(Token('+', TokenType.OPERATOR), [
                node.TermNode(Token('+', TokenType.OPERATOR), [
                    node.TermNode(Token('-', TokenType.OPERATOR), [
                        node.ValueNode(Token('3.14', TokenType.REAL))
                    ])
                ]),
                node.ValueNode(Token('1', TokenType.INTEGER))
            ])
        ]))
        self.assertEqual(build('1+++--2.2---+1'), node.ProgramNode(subs=[
            node.OpNode(Token('+', TokenType.OPERATOR), [
                node.ValueNode(Token('1', TokenType.INTEGER)),
                node.OpNode(Token('-', TokenType.OPERATOR), [
                    node.TermNode(Token('+', TokenType.OPERATOR), [
                        node.TermNode(Token('+', TokenType.OPERATOR), [
                            node.TermNode(Token('-', TokenType.OPERATOR), [
                                node.TermNode(Token('-', TokenType.OPERATOR), [
                                    node.ValueNode(Token('2.2', TokenType.REAL))
                                ])
                            ])
                        ])
                    ]),
                    node.TermNode(Token('-', TokenType.OPERATOR), [
                        node.TermNode(Token('-', TokenType.OPERATOR), [
                            node.TermNode(Token('+', TokenType.OPERATOR), [
                                node.ValueNode(Token('1', TokenType.INTEGER))
                            ])
                        ])
                    ])
                ])
            ])
        ]))
        self.assertEqual(build('-1*-2'), node.ProgramNode(subs=[
            node.OpNode(Token('*', TokenType.OPERATOR), [
                node.TermNode(Token('-', TokenType.OPERATOR), [
                    node.ValueNode(Token('1', TokenType.INTEGER))
                ]),
                node.TermNode(Token('-', TokenType.OPERATOR), [
                    node.ValueNode(Token('2', TokenType.INTEGER))
                ]),
            ])
        ]))
        self.assertEqual(build('4+2/2+1'), node.ProgramNode(subs=[
            node.OpNode(Token('+', TokenType.OPERATOR), [
                node.ValueNode(Token('4', TokenType.INTEGER)),
                node.OpNode(Token('+', TokenType.OPERATOR), [
                    node.OpNode(Token('/', TokenType.OPERATOR), [
                        node.ValueNode(Token('2', TokenType.INTEGER)),
                        node.ValueNode(Token('2', TokenType.INTEGER))
                    ]),
                    node.ValueNode(Token('1', TokenType.INTEGER))
                ])
            ])
        ]))
        self.assertEqual(build('2*((1+3)/2+1)'), node.ProgramNode(subs=[
            node.OpNode(Token('*', TokenType.OPERATOR), [
                node.ValueNode(Token('2', TokenType.INTEGER)),
                node.OpNode(Token('+', TokenType.OPERATOR), [
                    node.OpNode(Token('/', TokenType.OPERATOR), [
                        node.OpNode(Token('+', TokenType.OPERATOR), [
                            node.ValueNode(Token('1', TokenType.INTEGER)),
                            node.ValueNode(Token('3', TokenType.INTEGER))
                        ]),
                        node.ValueNode(Token('2', TokenType.INTEGER))
                    ]),
                    node.ValueNode(Token('1', TokenType.INTEGER))
                ])
            ])
        ]))
        self.assertEqual(build('2*10**2*2'), node.ProgramNode(subs=[
            node.OpNode(Token('*', TokenType.OPERATOR), [
                node.ValueNode(Token('2', TokenType.INTEGER)),
                node.OpNode(Token('*', TokenType.OPERATOR), [
                    node.OpNode(Token('**', TokenType.OPERATOR), [
                        node.ValueNode(Token('10', TokenType.INTEGER)),
                        node.ValueNode(Token('2', TokenType.INTEGER))
                    ]),
                    node.ValueNode(Token('2', TokenType.INTEGER))
                ])
            ])
        ]))

calculator_test_cases = [
    ('1+2', 3),
    ('-1+2', 1),
    ('+-3.14 + 1', -2.14),
    ('1+++--2.2---+1', 2.2),
    ('-1*-2', 2),
    ('4+2/2+1', 6),
    ('2*((1+3)/2+1)', 6),
    ('2*10**2*2', 400)
]

class InterpreterTest(unittest.TestCase):
    def test_numeric_expression(self):
        for expression, result in calculator_test_cases:
            self.assertAlmostEqual(execute(expression), result)

class MachineTest(unittest.TestCase):
    def test_run(self):
        for expression, result in calculator_test_cases:
            self.assertAlmostEqual(run(compile2bytes(expression)), result, delta=5)


if __name__ == '__main__':
    unittest.main()
