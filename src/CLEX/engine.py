class SecurityError(Exception):
    pass


class PrefixError(Exception):
    pass


class Engine:
    def __init__(self, functions, allowDunder=False, **whitelist):
        from re import compile, MULTILINE, DOTALL

        self.functions = functions
        self.dunder_pattern = compile(r"\b__[a-zA-Z0-9_]+__\b", MULTILINE | DOTALL)
        self.allowDunder = allowDunder
        self.whitelist = whitelist or {}
        self._compile_function_ops()

    def __call__(self, **inputs):
        return self.eval(**inputs)

    def eval(self, **inputs):
        actions = {
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

            '@': lambda x, y: list(x[y]),
            '^': lambda x, y: list(set(x) & set(y)),
            '!^': lambda x, y: list(set(x) - set(y)),
            '.': lambda x, y: [str(a).startswith(b) for a, b in zip(x,y)],
            
            'extern': lambda x, y, func: [func(a, b) for a, b in zip(x, y)]
        }

        _inputs = {**inputs}
        values = []

        for func in self.functions:
            prefix, value_name, op, v2, return_name = func
            input_value = _inputs[value_name]
            v2_data = self._resolve_v2_value(_inputs, v2, input_value)

            values = self._evaluate_op(actions, op, input_value, v2_data, prefix)
            _inputs[return_name] = values

        return values

    def _resolve_v2_value(self, inputs, v2_ref, input_value):
        if isinstance(v2_ref, str):
            try:
                return [float(v2_ref)] * len(input_value)
            except ValueError:
                return [v2_ref] * len(input_value)

        try:
            return [float(v2_ref)] * len(input_value)
        except (ValueError, TypeError):
            return inputs[v2_ref]

    def _compile_function_ops(self):
        for func in self.functions:
            op = func[2]
            if isinstance(op, list):
                external_ref = op[0] if op else None
                if isinstance(external_ref, str):
                    compiled_op = self._safe_eval(external_ref)
                    if isinstance(compiled_op, list):
                        compiled_op = compiled_op[0]
                    if isinstance(compiled_op, str):
                        compiled_op = eval(compiled_op, self.whitelist)
                    func[2] = ("extern", compiled_op)

    def _safe_eval(self, func_ref):
        if not self.allowDunder and self.dunder_pattern.search(func_ref):
            raise SecurityError(
                f"Dunder method detected in {func_ref}. If this is intentional, set 'allowDunder' = True"
            )

        return eval(func_ref, self.whitelist)

    def _evaluate_op(self, actions, op, input_value, v2_data, prefix):
        def evaluate():
            if isinstance(op, tuple):
                return actions["extern"](input_value, v2_data, op[1])

            elif op in actions:
                return actions[op](input_value, v2_data)
            
            else:
                raise TypeError(f"Unknown operator received: {op}")

        match prefix:
            case "&":
                return [input_value[i] for i, val in enumerate(evaluate()) if val]
            case "!&":
                return [input_value[i] for i, val in enumerate(evaluate()) if not val]
            case "_":
                return evaluate()
            case _:
                raise PrefixError(f"Unknown Prefix: {prefix}")