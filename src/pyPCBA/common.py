"""Shared symbolic conversion helpers for the pyPCBA package."""

from __future__ import annotations

import re

import sympy as sp

__all__ = ["eq2sympy"]


def _rewrite_special_operators(expression: sp.Expr) -> sp.Expr:
    """Translate circuit operator syntax into standard SymPy expressions."""
    if isinstance(expression, sp.Equality):
        return sp.Eq(
            _rewrite_special_operators(expression.lhs),
            _rewrite_special_operators(expression.rhs),
            evaluate=False,
        )

    if not hasattr(expression, "args") or not expression.args:
        return expression

    func_name = getattr(expression.func, "__name__", "")
    if getattr(expression, "is_BitOr", False) or func_name == "BitOr":
        if len(expression.args) != 2:
            raise ValueError("Bitwise OR operator expects exactly two operands.")
        left, right = expression.args
        return _rewrite_special_operators(right) / (
            _rewrite_special_operators(left) + _rewrite_special_operators(right)
        )

    if getattr(expression, "is_FloorDiv", False) or func_name in {"FloorDiv", "floor_div"}:
        if len(expression.args) != 2:
            raise ValueError("Floor-division operator expects exactly two operands.")
        left, right = expression.args
        left = _rewrite_special_operators(left)
        right = _rewrite_special_operators(right)
        return (left * right) / (left + right)

    rewritten_args = tuple(_rewrite_special_operators(arg) for arg in expression.args)
    try:
        return expression.func(*rewritten_args)
    except TypeError:
        return expression.func(*rewritten_args, evaluate=False)


def _rewrite_text_operators(text: str) -> str:
    """Rewrite circuit-specific operators into algebraic SymPy expressions."""
    rewritten = text.strip()
    if not rewritten:
        return rewritten

    rewritten = rewritten.replace("||", " // ")

    while True:
        new_text = re.sub(
            r"(?P<left>[^|/]+?)\s*\|\s*(?P<right>[^|/]+)",
            lambda match: f"(({match.group('right')})/(({match.group('left')})+({match.group('right')})))",
            rewritten,
        )
        if new_text == rewritten:
            break
        rewritten = new_text

    while True:
        new_text = re.sub(
            r"(?P<left>[^/]+?)\s*//\s*(?P<right>[^/]+)",
            lambda match: f"((({match.group('left')})*({match.group('right')}))/(({match.group('left')})+({match.group('right')})))",
            rewritten,
        )
        if new_text == rewritten:
            break
        rewritten = new_text

    return rewritten


def eq2sympy(equations: str | sp.Expr | sp.Equality) -> sp.Expr | sp.Equality:
    """Convert circuit-style operators into regular SymPy expressions.

    Args:
        equations: A string equation such as ``"R1 | R2 = 0.33"``, a SymPy
            expression, or a SymPy equality.

    Returns:
        A SymPy expression or equality with the special operators rewritten into
        standard arithmetic expressions.

    Raises:
        TypeError: If a non-SymPy or non-string object is supplied.
        ValueError: If the supplied string fails to parse into a valid SymPy
            expression.
    """
    if isinstance(equations, bool):
        raise TypeError("equations must be a string, SymPy expression, or SymPy equality.")

    if isinstance(equations, str):
        text = equations.strip()
        if not text:
            raise ValueError("equations must not be empty.")

        if "=" in text:
            left_text, right_text = text.split("=", 1)
            return sp.Eq(
                eq2sympy(_rewrite_text_operators(left_text.strip())),
                eq2sympy(_rewrite_text_operators(right_text.strip())),
                evaluate=False,
            )

        rewritten_text = _rewrite_text_operators(text)
        try:
            parsed_expression = sp.sympify(rewritten_text, evaluate=True)
        except (SyntaxError, TypeError, ValueError) as error:
            raise ValueError(f"Could not parse equation: {equations!r}") from error
        return _rewrite_special_operators(parsed_expression)

    if isinstance(equations, (sp.Expr, sp.Equality)):
        return _rewrite_special_operators(equations)

    raise TypeError("equations must be a string, SymPy expression, or SymPy equality.")
