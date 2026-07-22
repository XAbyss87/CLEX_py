import re
from typing import Any, List, Tuple

class SecurityError(Exception):
    pass


class PrefixError(Exception):
    pass


class Engine:
    """
    Engine to process a sequence of operations on input data.
    """

    def __init__(self, functions: List[Tuple], allow_dunder: bool = False, **whitelist: Any):
        self.functions = functions
        self.dunder_pattern = re.compile(r"\b__[a-zA-Z0-9_]+__\b", re.MULTILINE | re.DOTALL)
        self.allow_dunder = allow_dunder
        self.whitelist = whitelist or {}
        self._compile_function_ops()

        self._actions = {
            '+': lambda x, y: [a + b for a, b in zip(x, y)],
            '-': lambda x, y: [a - b for a, b in zip(x, y)],
            '*': lambda x, y: [a * b for a, b in zip(x, y)],
            '/': lambda x, y: [a / b for a, b in zip(x, y)],
            '%': lambda x, y: [a % b for a, b in zip(x, y)],
            '==': lambda x, y: [a == b for a, b in zip(x, y)],
            '>': lambda x, y: [a > b for a, b in zip(x, y)],
            '<': lambda x, y: [a < b for a, b in zip(x, y)],
            '>=': lambda x, y: [a >= b for a, b in zip(x, y)],
            '<=': lambda x, y: [a <= b for a, b in zip(x, y)],
            '!=': lambda x, y: [a != b for a, b in zip(x, y)],
            '@': lambda x, y: [x[i] for i in y],
            '^': lambda x, y: list(set(x) & set(y)),
            '!^': lambda x, y: list(set(x) - set(y)),
            ',': lambda x, y: [str(a).startswith(str(b)) for a, b in zip(x, y)],
            '.': lambda x, y: [str(a).endswith(str(b)) for a, b in zip(x, y)],
            '!': lambda x, _: x,
            '<>': lambda x, y: x + y,
            '#': lambda x, y: {a: b for a, b in zip(x, y)},
            'extern': lambda x, y, func: [func(a, b) for a, b in zip(x, y)]
        }

        self._prefix_handlers = {
            "&": lambda x, func: [x[i] for i, val in enumerate(func()) if val],
            "parse": lambda x, func: [x[i] for i, val in enumerate(func()) if val],
            "!&": lambda x, func: [x[i] for i, val in enumerate(func()) if not val],
            "neg_parse": lambda x, func: [x[i] for i, val in enumerate(func()) if not val],
            "_": lambda _, func: func(),
            "none": lambda _, func: func(),
            "?": lambda _, func: sorted(func()),
            "sort": lambda _, func: sorted(func()),
            "-": lambda _, func: list(reversed(func())),
            "reverse": lambda _, func: list(reversed(func())),
            "-?": lambda _, func: sorted(func(), reverse=True),
            "reverse_sort": lambda _, func: sorted(func(), reverse=True),
            "$": lambda _, func: sum(func()),
            "sum": lambda _, func: sum(func()),
            "length": lambda _, func: len(func() + 1),
            "|": lambda _, func: len(func()) + 1,
            "average": lambda _, func: sum(func()) / len(func()),
            "%": lambda _, func: sum(func()) / len(func()),
        }

    def __call__(self, **inputs: Any) -> Any:
        return self.eval(**inputs)

    def eval(self, **inputs: Any) -> Any:
        state = {**inputs}
        last_values = []

        for prefix, value_name, op, v2, return_name in self.functions:
            # Small helper
            def execute_op():
                v2_data = self._resolve_v2_value(state, v2, input_value)
                
                if isinstance(op, tuple):
                    return self._actions["extern"](input_value, v2_data, op[1])
                return self._actions[op](input_value, v2_data)
            
            input_value = state[value_name]

            if prefix in self._prefix_handlers:
                last_values = self._prefix_handlers[prefix](input_value, execute_op)
            else:
                raise PrefixError(f"Unknown Prefix: {prefix}")
            
            state[return_name] = last_values

        return last_values

    def _resolve_v2_value(self, state, v2_ref, input_data):
        try:
            v2_float = float(v2_ref)
            return [v2_float] * len(input_data)
        except ValueError:
            return state[v2_ref]

    def _compile_function_ops(self) -> None:
        for func in self.functions:
            if isinstance(op := func[2], list):
                # Parser gaurentees an op is present
                op = ("extern", self._safe_eval(op[0]))

    def _safe_eval(self, func_ref: str) -> Any:
        if not self.allow_dunder and self.dunder_pattern.search(func_ref):
            raise SecurityError(
                f"Dunder method detected in {func_ref}. Set 'allow_dunder' = True to enable."
            )
        return eval(func_ref, self.whitelist)