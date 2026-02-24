# 🔧 Mini Compiler & Interpreter

> A from-scratch interpreter with Lexer, Parser (Recursive Descent), AST builder, and Evaluator — supporting variables, arithmetic, conditionals, and loops.

---

## 📌 Description

Implements all core compiler phases in pure Python: lexical analysis (tokenizer), recursive descent parsing into an AST, and a tree-walk interpreter. Supports variables, arithmetic, comparisons, if/else, while loops, and a print statement — with a built-in REPL and token/AST inspection tools.

---

## 🛠️ Tech Stack

- Python 3.x
- Standard Library only (`re`, `dataclasses`)

---

## 🚀 Getting Started

```bash
git clone https://github.com/yourusername/mini-compiler.git
cd mini-compiler
python mini_compiler.py
```

---

## 💻 Supported Language Syntax

```js
// Variables and arithmetic
x = 5
y = x * 2 + 3 ** 2    // supports power operator
z = y % 4

// Conditionals
if (x > 3) {
    print(x)
} else {
    print(0)
}

// While loops
i = 0
while (i < 5) {
    print(i)
    i = i + 1
}
```

---

## 🔬 Features

| Feature | Details |
|---|---|
| REPL | Interactive line-by-line execution |
| Token Inspector | View lexer output for any expression |
| AST Inspector | View parsed syntax tree |
| Sample Programs | Fibonacci, Factorial, FizzBuzz, Expressions |
| Error Reporting | Line-numbered syntax and runtime errors |
| Safety | Infinite loop detection (>10000 iterations) |

---

## 📂 Project Structure

```
mini-compiler/
├── mini_compiler.py    # Lexer + Parser + AST + Interpreter
└── README.md
```

---

## 🧠 Compiler Phases Implemented

```
Source Code
   ↓
[Lexer] → Token Stream
   ↓
[Parser] → Abstract Syntax Tree (AST)
   ↓
[Interpreter] → Program Output
```

---

## 🧩 Concepts Covered

- Lexical analysis and tokenization
- Recursive Descent Parsing
- Abstract Syntax Trees (AST)
- Tree-walk interpretation
- Operator precedence and associativity
- Symbol tables (variable environment)

---

## 📄 License

MIT
