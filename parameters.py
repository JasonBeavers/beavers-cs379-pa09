from typing import Any, List, Tuple

from parser import BinOp, Number, Variable
from symtable import Environment


class Cell:
    """Given: a mutable box. Two names that share the SAME Cell are aliased."""

    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value = value


class FunctionDecl:
    """Given: a minimal function declaration -- params and a single expr body."""

    __slots__ = ("params", "body")

    def __init__(self, params: List[str], body) -> None:
        self.params = params
        self.body = body


def evaluate(node, env: Environment):
    """Given: evaluate a PA3 expression AST node against `env` (Cells are transparently dereferenced)."""
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Variable):
        val = env.resolve(node.name)
        return val.value if isinstance(val, Cell) else val
    if isinstance(node, BinOp):
        if node.op == "neg":
            return -evaluate(node.left, env)
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        return {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b}[node.op](left, right)
    raise ValueError(f"cannot evaluate node: {node!r}")


def assign_through(env: Environment, name: str, value: Any) -> None:
    """Given: write `value` into whatever Cell `name` resolves to (mutates in place, does not rebind)."""
    cell = env.resolve(name)
    if not isinstance(cell, Cell):
        raise TypeError(f"'{name}' is not bound to a Cell -- did you forget to wrap it?")
    cell.value = value


def bind_parameters(param_specs: List[Tuple[str, str]], arg_nodes: list, caller_env: Environment, callee_record) -> None:
    callee_record.pending_writeback = []

    for (param_name, mode), arg_node in zip(param_specs, arg_nodes):

        if mode == "value":
            value = evaluate(arg_node, caller_env)
            callee_record.locals_env.define(param_name, Cell(value))

        elif mode == "reference":
            if not isinstance(arg_node, Variable):
                raise TypeError(
                    "Reference arguments must be caller variables."
                )

            caller_cell = caller_env.resolve(arg_node.name)

            if not isinstance(caller_cell, Cell):
                raise TypeError(
                    f"'{arg_node.name}' is not bound to a Cell."
                )

            callee_record.locals_env.define(param_name, caller_cell)

        elif mode == "value-result":
            if not isinstance(arg_node, Variable):
                raise TypeError(
                    "Value-result arguments must be caller variables."
                )

            caller_cell = caller_env.resolve(arg_node.name)

            if not isinstance(caller_cell, Cell):
                raise TypeError(
                    f"'{arg_node.name}' is not bound to a Cell."
                )

            callee_record.locals_env.define(
                param_name, Cell(caller_cell.value)
            )

            callee_record.pending_writeback.append(
                (param_name, caller_cell)
            )

        else:
            raise ValueError(f"Unknown parameter mode: {mode}")


def commit_value_result(callee_record, caller_env: Environment) -> None:
    pending = getattr(callee_record, "pending_writeback", [])

    for param_name, caller_cell in pending:
        local_cell = callee_record.locals_env.resolve(param_name)

        if not isinstance(local_cell, Cell):
            raise TypeError(
                f"'{param_name}' is not bound to a Cell."
            )

        caller_cell.value = local_cell.value


class Closure:
    def __init__(self, declaration: FunctionDecl, defining_env: Environment) -> None:
        self.declaration = declaration
        self.defining_env = defining_env


    def call(self, args: list, caller_env: Environment):
        callee_env = Environment(parent=self.defining_env)

        for param_name, arg_value in zip(self.declaration.params, args):
            callee_env.define(param_name, Cell(arg_value))

        return evaluate(self.declaration.body, callee_env)
