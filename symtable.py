from typing import Optional

from parser import Assignment, BinOp, Declaration, Number, Program, Variable


class SemanticError(Exception):
    pass



class Environment:
    def __init__(self, parent: Optional["Environment"] = None) -> None:
        self.parent = parent
        self._names: dict = {}

    def define(self, name: str, value: object) -> None:
        if name in self._names:
            original = self._names[name]


            original_line = original if isinstance(original, int) else "unknown"
            raise SemanticError(
                f"Duplicate declaration of '{name}' "
                f"(line {value}; originally declared line {original_line})."
            )

        self._names[name] = value

    def resolve(self, name: str) -> object:
        if name in self._names:
            return self._names[name]

        if self.parent is not None:
            return self.parent.resolve(name)

        raise SemanticError(f"Undeclared variable '{name}'.")


def check_expr(expr, env):
    if isinstance(expr, Number):
        return

    if isinstance(expr, Variable):
        try:    
            env.resolve(expr.name)
        except SemanticError:
            raise SemanticError(f"Undeclared variable '{expr.name}' on line {expr.line}.")
        return

    if isinstance(expr, BinOp):
        check_expr(expr.left, env)
        check_expr(expr.right, env)
        return

def check_program(ast: Program) -> Environment:
    env = Environment()

    for statement in ast.statements:
        if isinstance(statement, Declaration):
            check_expr(statement.expr, env)
            env.define(statement.name, statement.line)

        elif isinstance(statement, Assignment):
            try:    
                env.resolve(statement.name)
            except SemanticError:
                raise SemanticError(f"Undeclared variable '{statement.name}' on line {statement.line}.")
            check_expr(statement.expr, env)

    return env