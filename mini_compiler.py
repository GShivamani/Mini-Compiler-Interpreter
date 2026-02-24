"""
Mini Compiler / Interpreter
Tokenizes, parses, and evaluates arithmetic + variable expressions.
Covers: Lexical Analysis, Parsing (Recursive Descent), AST, Evaluation.
"""

import re
from dataclasses import dataclass
from typing import Any, Optional


# ─────────────────────────────────────────────
# TOKENS
# ─────────────────────────────────────────────

class TokenType:
    NUMBER   = "NUMBER"
    IDENT    = "IDENT"
    PLUS     = "PLUS"
    MINUS    = "MINUS"
    MUL      = "MUL"
    DIV      = "DIV"
    MOD      = "MOD"
    POW      = "POW"
    ASSIGN   = "ASSIGN"
    EQ       = "EQ"
    NEQ      = "NEQ"
    LT       = "LT"
    GT       = "GT"
    LTE      = "LTE"
    GTE      = "GTE"
    LPAREN   = "LPAREN"
    RPAREN   = "RPAREN"
    PRINT    = "PRINT"
    IF       = "IF"
    ELSE     = "ELSE"
    WHILE    = "WHILE"
    LBRACE   = "LBRACE"
    RBRACE   = "RBRACE"
    SEMICOL  = "SEMICOL"
    EOF      = "EOF"


@dataclass
class Token:
    type: str
    value: Any
    line: int = 0


# ─────────────────────────────────────────────
# LEXER
# ─────────────────────────────────────────────

KEYWORDS = {"print", "if", "else", "while"}

TOKEN_PATTERNS = [
    (r'\d+(\.\d+)?',  TokenType.NUMBER),
    (r'[a-zA-Z_]\w*', TokenType.IDENT),
    (r'==',           TokenType.EQ),
    (r'!=',           TokenType.NEQ),
    (r'<=',           TokenType.LTE),
    (r'>=',           TokenType.GTE),
    (r'<',            TokenType.LT),
    (r'>',            TokenType.GT),
    (r'=',            TokenType.ASSIGN),
    (r'\+',           TokenType.PLUS),
    (r'-',            TokenType.MINUS),
    (r'\*\*',         TokenType.POW),
    (r'\*',           TokenType.MUL),
    (r'/',            TokenType.DIV),
    (r'%',            TokenType.MOD),
    (r'\(',           TokenType.LPAREN),
    (r'\)',           TokenType.RPAREN),
    (r'\{',           TokenType.LBRACE),
    (r'\}',           TokenType.RBRACE),
    (r';',            TokenType.SEMICOL),
]


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.tokens = []

    def error(self, char):
        raise SyntaxError(f"[Lexer] Unknown character '{char}' at line {self.line}")

    def tokenize(self):
        while self.pos < len(self.source):
            # Skip whitespace
            if self.source[self.pos].isspace():
                if self.source[self.pos] == '\n':
                    self.line += 1
                self.pos += 1
                continue
            # Skip comments
            if self.source[self.pos:self.pos+2] == '//':
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.pos += 1
                continue

            matched = False
            for pattern, ttype in TOKEN_PATTERNS:
                m = re.match(pattern, self.source[self.pos:])
                if m:
                    val = m.group(0)
                    if ttype == TokenType.NUMBER:
                        val = float(val) if '.' in val else int(val)
                    elif ttype == TokenType.IDENT and val in KEYWORDS:
                        ttype = val.upper()
                    self.tokens.append(Token(ttype, val, self.line))
                    self.pos += len(m.group(0))
                    matched = True
                    break
            if not matched:
                self.error(self.source[self.pos])

        self.tokens.append(Token(TokenType.EOF, None, self.line))
        return self.tokens


# ─────────────────────────────────────────────
# AST NODES
# ─────────────────────────────────────────────

@dataclass
class NumberNode:
    value: float

@dataclass
class VarNode:
    name: str

@dataclass
class BinOpNode:
    left: Any
    op: str
    right: Any

@dataclass
class UnaryNode:
    op: str
    operand: Any

@dataclass
class AssignNode:
    name: str
    value: Any

@dataclass
class PrintNode:
    expr: Any

@dataclass
class IfNode:
    condition: Any
    then_body: list
    else_body: Optional[list]

@dataclass
class WhileNode:
    condition: Any
    body: list

@dataclass
class BlockNode:
    statements: list


# ─────────────────────────────────────────────
# PARSER (Recursive Descent)
# ─────────────────────────────────────────────

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def eat(self, ttype):
        tok = self.current()
        if tok.type != ttype:
            raise SyntaxError(f"[Parser] Expected {ttype}, got {tok.type} ('{tok.value}') at line {tok.line}")
        self.pos += 1
        return tok

    def parse(self):
        stmts = []
        while self.current().type != TokenType.EOF:
            stmts.append(self.statement())
        return BlockNode(stmts)

    def statement(self):
        tok = self.current()

        if tok.type == "PRINT":
            self.pos += 1
            self.eat(TokenType.LPAREN)
            expr = self.expression()
            self.eat(TokenType.RPAREN)
            self.optional_semicolon()
            return PrintNode(expr)

        elif tok.type == "IF":
            return self.if_stmt()

        elif tok.type == "WHILE":
            return self.while_stmt()

        elif tok.type == TokenType.IDENT and self.tokens[self.pos+1].type == TokenType.ASSIGN:
            name = self.eat(TokenType.IDENT).value
            self.eat(TokenType.ASSIGN)
            val = self.expression()
            self.optional_semicolon()
            return AssignNode(name, val)

        else:
            expr = self.expression()
            self.optional_semicolon()
            return expr

    def optional_semicolon(self):
        if self.current().type == TokenType.SEMICOL:
            self.pos += 1

    def if_stmt(self):
        self.eat("IF")
        self.eat(TokenType.LPAREN)
        cond = self.expression()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        then_body = []
        while self.current().type != TokenType.RBRACE:
            then_body.append(self.statement())
        self.eat(TokenType.RBRACE)
        else_body = None
        if self.current().type == "ELSE":
            self.pos += 1
            self.eat(TokenType.LBRACE)
            else_body = []
            while self.current().type != TokenType.RBRACE:
                else_body.append(self.statement())
            self.eat(TokenType.RBRACE)
        return IfNode(cond, then_body, else_body)

    def while_stmt(self):
        self.eat("WHILE")
        self.eat(TokenType.LPAREN)
        cond = self.expression()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        body = []
        while self.current().type != TokenType.RBRACE:
            body.append(self.statement())
        self.eat(TokenType.RBRACE)
        return WhileNode(cond, body)

    def expression(self):
        return self.comparison()

    def comparison(self):
        left = self.additive()
        ops = {TokenType.EQ: "==", TokenType.NEQ: "!=",
               TokenType.LT: "<", TokenType.GT: ">",
               TokenType.LTE: "<=", TokenType.GTE: ">="}
        while self.current().type in ops:
            op = ops[self.current().type]
            self.pos += 1
            right = self.additive()
            left = BinOpNode(left, op, right)
        return left

    def additive(self):
        left = self.multiplicative()
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current().value
            self.pos += 1
            right = self.multiplicative()
            left = BinOpNode(left, op, right)
        return left

    def multiplicative(self):
        left = self.power()
        while self.current().type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            op = self.current().value
            self.pos += 1
            right = self.power()
            left = BinOpNode(left, op, right)
        return left

    def power(self):
        base = self.unary()
        if self.current().type == TokenType.POW:
            self.pos += 1
            exp = self.power()
            return BinOpNode(base, "**", exp)
        return base

    def unary(self):
        if self.current().type == TokenType.MINUS:
            self.pos += 1
            return UnaryNode("-", self.primary())
        return self.primary()

    def primary(self):
        tok = self.current()
        if tok.type == TokenType.NUMBER:
            self.pos += 1
            return NumberNode(tok.value)
        elif tok.type == TokenType.IDENT:
            self.pos += 1
            return VarNode(tok.value)
        elif tok.type == TokenType.LPAREN:
            self.pos += 1
            expr = self.expression()
            self.eat(TokenType.RPAREN)
            return expr
        raise SyntaxError(f"[Parser] Unexpected token {tok.type} ('{tok.value}') at line {tok.line}")


# ─────────────────────────────────────────────
# EVALUATOR / INTERPRETER
# ─────────────────────────────────────────────

class Interpreter:
    def __init__(self):
        self.env = {}
        self.output = []

    def eval(self, node):
        if isinstance(node, BlockNode):
            result = None
            for stmt in node.statements:
                result = self.eval(stmt)
            return result

        elif isinstance(node, NumberNode):
            return node.value

        elif isinstance(node, VarNode):
            if node.name not in self.env:
                raise NameError(f"[Runtime] Undefined variable '{node.name}'")
            return self.env[node.name]

        elif isinstance(node, AssignNode):
            val = self.eval(node.value)
            self.env[node.name] = val
            return val

        elif isinstance(node, BinOpNode):
            l = self.eval(node.left)
            r = self.eval(node.right)
            ops = {
                "+": lambda a, b: a + b,
                "-": lambda a, b: a - b,
                "*": lambda a, b: a * b,
                "/": lambda a, b: a / b if b != 0 else (_ for _ in ()).throw(ZeroDivisionError("Division by zero")),
                "%": lambda a, b: a % b,
                "**": lambda a, b: a ** b,
                "==": lambda a, b: int(a == b),
                "!=": lambda a, b: int(a != b),
                "<": lambda a, b: int(a < b),
                ">": lambda a, b: int(a > b),
                "<=": lambda a, b: int(a <= b),
                ">=": lambda a, b: int(a >= b),
            }
            return ops[node.op](l, r)

        elif isinstance(node, UnaryNode):
            val = self.eval(node.operand)
            return -val if node.op == "-" else val

        elif isinstance(node, PrintNode):
            val = self.eval(node.expr)
            result = int(val) if isinstance(val, float) and val.is_integer() else val
            print(f"  >> {result}")
            self.output.append(result)
            return result

        elif isinstance(node, IfNode):
            if self.eval(node.condition):
                for stmt in node.then_body:
                    self.eval(stmt)
            elif node.else_body:
                for stmt in node.else_body:
                    self.eval(stmt)

        elif isinstance(node, WhileNode):
            iterations = 0
            while self.eval(node.condition):
                iterations += 1
                if iterations > 10000:
                    raise RuntimeError("Infinite loop detected (>10000 iterations)")
                for stmt in node.body:
                    self.eval(stmt)


# ─────────────────────────────────────────────
# REPL + FILE MODE
# ─────────────────────────────────────────────

def run(source, interpreter=None):
    if interpreter is None:
        interpreter = Interpreter()
    try:
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        interpreter.eval(ast)
    except (SyntaxError, NameError, ZeroDivisionError, RuntimeError) as e:
        print(f"  ❌ {e}")
    return interpreter


def show_tokens(source):
    try:
        tokens = Lexer(source).tokenize()
        print("\n  📋 Tokens:")
        for t in tokens:
            if t.type != TokenType.EOF:
                print(f"    {t.type:12s} | {repr(t.value)}")
    except SyntaxError as e:
        print(f"  ❌ {e}")


def show_ast(source):
    try:
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        import pprint
        print("\n  🌳 AST:")
        pprint.pprint(ast, indent=2)
    except (SyntaxError, Exception) as e:
        print(f"  ❌ {e}")


SAMPLE_PROGRAMS = {
    "1": ("Fibonacci", """
// Fibonacci sequence
a = 0
b = 1
i = 0
while (i < 10) {
    print(a)
    temp = a + b
    a = b
    b = temp
    i = i + 1
}
"""),
    "2": ("Factorial", """
// Factorial of 6
n = 6
result = 1
i = 1
while (i <= n) {
    result = result * i
    i = i + 1
}
print(result)
"""),
    "3": ("FizzBuzz", """
// FizzBuzz 1-15
i = 1
while (i <= 15) {
    print(i)
    i = i + 1
}
"""),
    "4": ("Expressions", """
x = 2 ** 10
y = x / 4 + 3 * 5
z = y % 7
print(x)
print(y)
print(z)
"""),
}


def main():
    print("=" * 55)
    print("  🔧 Mini Compiler & Interpreter")
    print("=" * 55)

    interpreter = Interpreter()

    while True:
        print("\n  1. REPL (interactive mode)")
        print("  2. Run sample program")
        print("  3. Show tokens (lexer output)")
        print("  4. Show AST (parser output)")
        print("  5. Exit")

        choice = input("\n  Choice: ").strip()

        if choice == "1":
            print("\n  📝 REPL Mode (type 'exit' to quit, 'reset' to clear vars)")
            print("  Supported: variables, arithmetic, if/else, while, print()")
            while True:
                try:
                    line = input("  >> ").strip()
                    if line == "exit":
                        break
                    elif line == "reset":
                        interpreter = Interpreter()
                        print("  Variables cleared.")
                    elif line == "vars":
                        print(f"  Variables: {interpreter.env}")
                    elif line:
                        run(line, interpreter)
                except (KeyboardInterrupt, EOFError):
                    break

        elif choice == "2":
            print("\n  Sample Programs:")
            for k, (name, _) in SAMPLE_PROGRAMS.items():
                print(f"    {k}. {name}")
            sel = input("  Choose: ").strip()
            if sel in SAMPLE_PROGRAMS:
                name, code = SAMPLE_PROGRAMS[sel]
                print(f"\n  Running: {name}")
                print("  " + "-" * 40)
                print(f"  Code:\n{code}")
                print("  Output:")
                run(code)

        elif choice == "3":
            code = input("  Enter expression: ").strip()
            show_tokens(code)

        elif choice == "4":
            code = input("  Enter expression: ").strip()
            show_ast(code)

        elif choice == "5":
            print("  Goodbye!")
            break


if __name__ == "__main__":
    main()
