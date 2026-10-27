from dataclasses import dataclass, field
from typing import List

from lexer import Token, tokenize


@dataclass
class Program:
    statements: list


@dataclass
class Declaration:
    name: str
    expr: object
    line: int


@dataclass
class Assignment:
    name: str
    expr: object
    line: int


@dataclass
class BinOp:
    op: str
    left: object
    right: object
    line: int


@dataclass
class Number:
    value: int
    line: int


@dataclass
class Variable:
    name: str
    line: int


class ParseError(Exception):
    pass


class _ParserState:
    """Given: a small cursor wrapper over the token list. Not required to use, but handy."""

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, type_: str) -> Token:
        tok = self.peek()
        if tok.type != type_:
            raise ParseError(f"Line {tok.line}: expected {type_}, found {tok.type} ({tok.lexeme!r}).")
        return self.advance()


def parse_factor(state: _ParserState):
    if state.peek().type == "NUMBER":
        tok = state.advance()
        return Number(int(tok.lexeme), tok.line)

    elif state.peek().type == "IDENT":
        tok = state.advance()
        return Variable(tok.lexeme, tok.line)

    elif state.peek().type == "LPAREN":
        state.advance()
        node = parse_expr(state)
        state.expect("RPAREN")
        return node
    else:
        tok = state.peek()
        raise ParseError(
            f"Line {tok.line}: expected NUMBER, IDENT, or LPAREN, "
            f"found {tok.type} ({tok.lexeme!r})."
        )


def parse_term(state: _ParserState):
    node = parse_factor(state)

    while state.peek().type in ("STAR", "SLASH"):
        op_tok = state.advance()
        right = parse_factor(state)
        node = BinOp(op_tok.lexeme, node, right, op_tok.line)

    return node


def parse_expr(state: _ParserState):
    node = parse_term(state)

    while state.peek().type in ("PLUS", "MINUS"):
        op_tok = state.advance()
        right = parse_term(state)
        node = BinOp(op_tok.lexeme, node, right, op_tok.line)

    return node


def parse_declaration(state: _ParserState) -> Declaration:
    state.expect("LET")

    name_tok = state.expect("IDENT")
    state.expect("ASSIGN")

    expr = parse_expr(state)

    state.expect("SEMI")

    return Declaration(name_tok.lexeme, expr, name_tok.line)


def parse_assignment(state: _ParserState) -> Assignment:
    name_tok = state.expect("IDENT")
    state.expect("ASSIGN")

    expr = parse_expr(state)

    state.expect("SEMI")

    return Assignment(name_tok.lexeme, expr, name_tok.line)


def parse_statement(state: _ParserState):
    if state.peek().type == "LET":
        return parse_declaration(state)

    elif state.peek().type == "IDENT":
        return parse_assignment(state)

    else:
        tok = state.peek()
        raise ParseError(
            f"Line {tok.line}: expected LET or IDENT, "
            f"found {tok.type} ({tok.lexeme!r})."
        )


def parse_program(state: _ParserState) -> Program:
    statements = []

    while state.peek().type != "EOF":
        statements.append(parse_statement(state))

    return Program(statements)


def parse(tokens: List[Token]) -> Program:
    state = _ParserState(tokens)
    return parse_program(state)
