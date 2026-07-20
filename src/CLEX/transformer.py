from lark import Transformer


class EngineFormatter(Transformer):
    def CNAME(self, token):
        return token.value

    def NUMBER(self, token):
        return int(token.value)

    def prefix(self, children):
        return children[0].value if children else "_"

    def OPERATOR(self, token):
        return token.value

    def FUNC_REF(self, token):
        return [token.value]

    def operation(self, children):
        return children[0]

    def value(self, children):
        return children[0]

    def return_rule(self, children):
        value = children[0] if children else None
        return value if value else "_"
    
    def STRING(self, token):
        if hasattr(token, "value"):
            value = token.value
        elif isinstance(token, list):
            value = "".join(str(item) for item in token)
        else:
            value = str(token)

        if len(value) >= 2 and value[0] in {'"', "'"} and value[-1] == value[0]:
            return value[1:-1]
        return value

    def expr(self, children):
        return children

    def start(self, children):
        prefix = children[0]
        expr_parts = children[1]
        current_step = [prefix, *expr_parts]

        if len(children) == 2:
            return [current_step]

        next_steps = children[2]
        return [current_step] + next_steps