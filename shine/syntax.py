from lark import Lark, Transformer
from observable import Observable

grammar = r"""
%import common.WS
%ignore WS

%import common.CNAME
%import common.NUMBER
%import common.ESCAPED_STRING

?start: program

program: (expr ";")*

VARIABLE: CNAME

?expr: VARIABLE -> variable
     | NUMBER -> number
     | ESCAPED_STRING -> string
     | function_call
     | assignment

function_call: VARIABLE "(" [expr ("," expr)*] ")"
assignment: VARIABLE "=" expr
"""


class Variable:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'Variable({self.name})'

    def eval(self, env):
        return env[self.name]


class FunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f'FunctionCall({self.name}, {self.args})'

    def eval(self, env):
        return Observable.list(env[self.name], *[arg.eval(env) for arg in self.args]).map(lambda args: args[0](*args[1:]))


class Assignment:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f'Assignment({self.name}, {self.value})'

    def eval(self, env):
        if self.name not in env:
            env[self.name] = self.value.eval(env)
        else:
            # TODO: is this logically sound as an observable replacement semantic?
            env[self.name].set(self.value.eval(env).get())


class Program:
    def __init__(self, exprs):
        self.exprs = exprs

    def __repr__(self):
        return f'Program({self.exprs})'

    def eval(self, env):
        return [expr.eval(env) for expr in self.exprs]


class Literal:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'Literal({self.value})'

    def eval(self, env):
        return Observable(self.value)


class SyntaxTransformer(Transformer):
    def VARIABLE(self, token):
        return str(token)

    def variable(self, token):
        return Variable(token[0])

    def number(self, token):
        return Literal(int(token[0]))

    def string(self, token):
        return Literal(str(token[0]))

    def function_call(self, tokens):
        return FunctionCall(tokens[0], tokens[1:])

    def assignment(self, tokens):
        return Assignment(tokens[0], tokens[1])

    def program(self, tokens):
        return Program(tokens)


parser = Lark(grammar, parser='lalr', transformer=SyntaxTransformer())


def parse(code):
    return parser.parse(code)


if __name__ == '__main__':
    code = """
    x = 5;
    y = add(3, x);
    print(y);
    x = 10;
    x = 13;
    x = 15;
    """

    parsed = parse(code)

    env = {
        'add': Observable(lambda x, y: x + y),
        'print': Observable(lambda x: print(x))
    }

    parsed.eval(env)
