from lark import Lark

try:
    from .transformer import EngineFormatter
    from .engine import Engine
except ImportError:  # pragma: no cover - fallback for direct script execution
    from transformer import EngineFormatter
    from engine import Engine

grammar = rf"""
start: prefix "(" expr ")" ("->" start)?
expr: CNAME operation value return_rule

value: CNAME | NUMBER | STRING
return_rule: ":" | ";" CNAME

operation: OPERATOR | FUNC_REF

STRING: /"[^"\\]*(?:\\.[^"\\]*)*"|'[^'\\]*(?:\\.[^'\\]*)*'/

prefix: PREFIX?
PREFIX.2: "!&" | "&"

OPERATOR: "+" | "-" | "*" | "/" | "%" | "==" | "<" | ">" | "<=" | ">=" | "!=" | "^" | "!^" | "."

FUNC_REF: /\[[^\]]+\]/

%import common.NUMBER
%import common.WS
%import common.CNAME
%ignore WS
"""

PARSER = Lark(grammar, start="start")
TRANSFORMER = EngineFormatter()


def expression(expr, allowDunder=False, **whitelist):
    """Parse a CLEX expression string and return an executable Engine.

    Any keyword arguments supplied here are merged into the evaluation
    namespace used by the engine. To keep compatibility with older calls, a
    keyword named ``whitelist`` may also be passed as a mapping alias.

    Args:
        expr: The CLEX expression string to parse.
        allowDunder: Whether to allow dunder-style names such as __getitem__
            during evaluation. Disabled by default for safety.
        **whitelist: Names to expose to eval for lambda/function references
            used inside the expression. A keyword named ``whitelist`` may also
            be used as a mapping alias for the same namespace.

    Returns:
        An Engine instance bound to the parsed expression.
    """
    ast = PARSER.parse(expr)
    code = TRANSFORMER.transform(ast)
    namespace = dict(whitelist.pop("whitelist", {}) or {})
    namespace.update(whitelist)
    return Engine(code, allowDunder=allowDunder, **namespace)
