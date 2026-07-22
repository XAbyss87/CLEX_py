# CLEX

CLEX stands for "Chained Lambda Expressions".

This is a small utility for writing simple data transformation steps as a readable string. It is handy when a chain of operations starts to look more complicated than the actual logic behind it.

> A quick example of the kind of thing this helps with.


```python
# plain Python
result = list(map(lambda r: r * 10, filter(lambda r: r > 3, map(lambda x: x + 1, [1, 2, 3, 4]))))
print(result)  # [40, 50]
```

That gets messy fast. With CLEX, the same idea is a bit easier to read:

```python
from CLEX.parser import expression

expr = expression("(x + 1; r) -> &(r > 3; r) -> (r * 10; r)")
print(expr(x=[1, 2, 3, 4]))  # [40, 50]
```

A typical example looks like this:

```python
from CLEX.parser import expression

expr = expression("(x + 1:)")
result = expr(x=[1, 2, 3])
print(result)  # [2, 3, 4]
```

You can also run the same expression with the `eval()` method:

```python
from CLEX.parser import expression

expr = expression("(x + 1:)")
result = expr.eval(x=[1, 2, 3])
print(result)  # [2, 3, 4]
```

---

## Installation

```bash
pip install clex-py
```

---

## How it works

A CLEX expression is made of one or more steps. Each step is written in a compact form that looks like this:

```text
(input operation value; output_name)
```

The pieces are:

- `input`: the name of the current input source. In the first step, this is usually one of the keyword arguments you pass when calling the expression.
- `operation`: the thing to do, such as `+`, `-`, `>`, `@`, or a lambda reference.
- `value`: the value to use for the operation.
- `output_name`: the name to store the result under for later steps.

If you do not want to give the result a custom name, you can use the `:` shortcut.

```text
(input operation value:)
```

That stores the result in the default `_` register instead of a named variable. The `_` register can be used in later steps if you want, but the most common use is at the end of a chain where you do not need a dedicated return name.

## Anatomy of a Step

A step is basically a small function description written in one line.

The general shape is:

```text
(input operation value; output_name)
```

and the shorthand form is:

```text
(input operation value:)
```

Here is what each piece means in practice:

- `input` is the current value source. On the first step, that is usually the name you pass when you call the expression, like `x`. On later steps, it can be the output from the previous step or the `_` register.
- `operation` is the action to apply. This can be one of the built-in operators, or a lambda-style function reference written in square brackets.
- `value` is the right-hand operand. It can be a literal, another value, or something that the engine resolves from the current execution context.
- `output_name` is optional. If you provide one, the result of that step is stored there and can be used in the next step. If you use `:`, the result goes to the default `_` register instead.

The `:` shortcut is mostly useful when you do not need a named intermediate result. It is especially convenient for the last step in a chain, because you can just let the result land in `_` and return it directly.

## Chaining steps

You can chain steps with `->`.

```python
from CLEX.parser import expression

expr = expression("(x + 1; r) -> (r * 2; r)")
print(expr(x=[1, 2, 3]))  # [4, 6, 8]
```

Each step uses the output from the previous one.

---

## Prefix system

CLEX also has a small prefix system. Prefixes are built-in helpers that act on the result of an expression step.

The built-in prefixes are:

| Prefix | Meaning |
| --- | --- |
| `&` / `parse` | keep values where result is truthy |
| `!&` / `neg_parse` | keep values where result is falsy |
| `_` / `none` | raw results |
| `?` / `sort` | sorted data |
| `-` / `reverse` | reversed data |
| `-?` / `reverse_sort` | reverse-sorted data |
| `$` / `sum` | sum of data |
| `\|` / `length` | length of data + 1 |
| `%` / `average` | average of data |

---

## Supported operations

### Arithmetic

| Operator | Meaning |
| --- | --- |
| `+` | addition |
| `-` | subtraction |
| `*` | multiplication |
| `/` | division |
| `%` | modulus |

### Comparison

These operators compare values and return `True` or `False`. They are not filters by themselves; they simply produce boolean results that can be used in a step or with a prefix.

| Operator | Meaning |
| --- | --- |
| `==` | equal |
| `!=` | not equal |
| `>` | greater than |
| `<` | less than |
| `>=` | greater than or equal |
| `<=` | less than or equal |

### Collection and string operations

| Operator | Meaning |
| --- | --- |
| `^` | set intersection |
| `!^` | set difference |
| `,` | startswith check |
| `.` | endswith check |
| `<>` | concatenation |
| `#` | create dictionary |

---

## Lambda functions

You can also use a lambda-style function reference inside a step.

```python
from CLEX.parser import expression

expr = expression("(x [lambda x, y: x + y] 1; r)")
print(expr(x=[1, 2, 3]))  # [2, 3, 4]
```

The lambda should accept two arguments. The first one is the current input element, and the second is the value supplied in the step.

---

## Running an expression

There are two common ways to execute a compiled expression:

```python
from CLEX.parser import expression

expr = expression("(x + 1:)")

expr(x=[1, 2, 3])
expr.eval(x=[1, 2, 3])
```

Both forms run the expression with the keyword arguments you provide.

---

## A fuller example

```python
from CLEX.parser import expression

expr = expression("(x + 1; r) -> &(r > 3; r) -> (r * 10; r)")
print(expr(x=[1, 2, 3, 4]))  # [40, 50]
```

That is mostly the same shape as the earlier examples: transform, apply a prefix, then transform again.

---

## Notes on safety

Lambda expressions are evaluated through Python's `eval()` machinery. Dunder-style names are blocked by default unless you explicitly allow them, and built-in methods are also disabled by default.

To allow any functions inside a lambda expression, you must explicitly pass them as a dictionary to the `whitelist` argument of `expression`.

That means this is fine for ordinary local use, but you should be careful about passing untrusted expressions around.

---

## License

This project is licensed under the GNU General Public License v3.0.
