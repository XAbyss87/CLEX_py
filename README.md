# CLEX (Chained-Lambda-Expressions)

**CLEX** is a lightweight, string-based Domain Specific Language (DSL) for building clean, readable functional pipelines in Python.

If you've ever chained multiple `map`, `filter`, or `zip` calls together, you know how quickly things become unreadable:

```python
result = list(map(lambda x: x * 2, filter(lambda x: x > 2, data)))
```

CLEX replaces this with a **structured, expressive pipeline string** that is easier to read, write, and maintain.

---

## Installation

```bash
pip install clex_py
```

---

## Quick Start

```python
from CLEX.parser import expression

# Compile a pipeline
add_one = expression("(x + 1:)")

# Execute it
result = add_one(x=[1, 2, 3, 4, 5])
print(result)  # [2, 3, 4, 5, 6]
```

---

## Core Concept

A CLEX pipeline is a **chain of small, single-purpose operations**, written inside a string.

### Function Format

```text
(input operation value; return_variable)
```

Shortcut:

```text
(input operation value:)
```

→ Automatically assigns the result to the default register `_`

---

## Anatomy of a Function

Each function has four parts:

1. **Input Iterable (`x`)**

   * The active dataset

2. **Operation**

   * The transformation, condition, or function applied

3. **Acting Value**

   * A scalar (broadcasted), or another iterable (zipped)

4. **Return Variable**

   * Where the result is stored

---

## Execution Model

* Operations run **element-wise**
* Scalars are automatically **broadcasted**
* Iterables are **zipped together**
* Execution stops at the **shortest iterable**
* The final step’s result is automatically returned

---

## Operators

### Arithmetic

| Operator | Behavior                          |
| -------- | --------------------------------- |
| +        | Addition                          |
| -        | Subtraction                       |
| *        | Multiplication                    |
| /        | Division (skips division by zero) |
| %        | Modulus                           |

---

### Comparison (Filtering)

Comparison operators act as filters:

| Operator | Behavior                 |
| -------- | ------------------------ |
| >        | Keep values greater than |
| <        | Keep values less than    |
| >=       | Keep values ≥            |
| <=       | Keep values ≤            |
| =        | Keep equal values        |
| !=       | Keep non-equal values    |

---

### Advanced Operations

| Operator | Behavior                              |
| -------- | ------------------------------------- |
| @        | Index access (`v1[v2]`)               |
| ^        | Intersection                          |
| !^       | Difference                            |
| .        | Startswith check (returns True/False) |

---

## Prefixes
They are built-in functions that add extra behaviour to your functions and act directly on the result.
Simply put the Prefix before the function body like so:

~~~python
"_Prefix_(Function)"
~~~

The currently supported Prefixes are:

| Prefix | Behaviour|
|--------|----------|
| &      | Filter Truthy ('v1[i] if v2[i]')|
| !&     | Filter Falsy ('v1[i] if not v2[i]')|

---

## Chaining Pipelines

Use `->` to chain operations:

```python
pipeline = expression("(x + 1; r) -> (r + 2; r)")
result = pipeline(x=[1, 2, 3])
```

---

## Example: Filtering Even Numbers

```python
from CLEX import expression

is_even = expression("!&(x % 2:)")

result = is_even(x=[1, 2, 3, 4, 5])
print(result)  # [2, 4]
```

---

## Custom Lambda Functions

CLEX supports user-defined transformations using square-bracket lambda syntax:

```python
expr = expression("(x [lambda x, y: x + 1] 1; r)")
```
- Note that lambdas are called for each element in an iterable passed as the first parameter with the second being the scalar.
### Requirements

* Must accept **two parameters**
* Must return an **iterable**
* Should produce results compatible with element-wise execution

---

## Safety Model

Lambda expressions are executed using Python’s `eval`, but with strict controls:

* Built-in functions are **disabled by default**
* Safe functions can be enabled via a **whitelist**
* Dunder methods are blocked unless explicitly allowed

This ensures controlled execution of dynamic expressions.

---

## Parser & Engine

CLEX uses a modern parsing system designed for flexibility and performance:

* Built with **Lark**
* Supports arbitrarily long variable names
* Optimized execution pipeline
* Prefix-based result filtering system

---

## Design Philosophy

CLEX is built around a few core ideas:

* **Clarity over nesting**
* **Composable transformations**
* **Minimal syntax, maximum expressiveness**
* **Safe execution of dynamic logic**

---

## Roadmap

* Port to Java, C#, and JavaScript
* Expand built-in operations
* Improve runtime performance and safety
* Enable deeper integration with Python functions

---

## Contributing

Contributions, issues, and suggestions are welcome.

---

## Summary

CLEX provides:

* A clean DSL for functional pipelines
* A readable alternative to nested functional code
* Safe execution of dynamic expressions
* Extensible and composable transformations

It’s designed for developers who want **powerful data transformations without sacrificing readability**.
