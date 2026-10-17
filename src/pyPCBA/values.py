"""Value optimization and symbolic utility functions."""

from __future__ import annotations

from itertools import product
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
import sympy as sp

__all__ = ["optimize"]


def optimize(
    equations: sp.Equality | Sequence[sp.Equality],
    series: Iterable[float] | np.ndarray,
    num_solutions: int = 10,
) -> pd.DataFrame:
    """Find preferred-value assignments that best satisfy symbolic equations.

    Each symbol in the equations is treated as an optimization variable, and
    every variable is assigned a value from ``series``. The function evaluates
    all possible assignments and ranks them by the sum of squared relative
    residuals:

    ``error = sum(((left_hand_side - right_hand_side) / right_hand_side) ** 2)``

    Args:
        equations: One SymPy equality or a sequence of equalities. Every free
            symbol in these equations is treated as a variable.
        series: Non-empty one-dimensional iterable of positive numeric values
            allowed for each variable.
        num_solutions: Maximum number of ranked solutions to return. Defaults
            to 10.

    Returns:
        A pandas DataFrame with one solution per row. Columns are ``Rank``,
        one column named after each variable in symbol-name order, and
        ``error``.

    Raises:
        TypeError: If ``equations`` contains non-equalities or the input
            container types are unsupported.
        ValueError: If inputs are empty or invalid, or no candidate assignment
            can be evaluated with the relative-error metric.

    Example:
        >>> from sympy import Eq, symbols
        >>> from pyPCBA.values import optimize
        >>> r1, r2 = symbols("R1 R2")
        >>> optimize(Eq(r2 / (r1 + r2), 0.5), [100, 120, 150])
    """
    if isinstance(equations, sp.Equality):
        equation_list = [equations]
    elif isinstance(equations, Sequence) and not isinstance(equations, (str, bytes)):
        equation_list = list(equations)
    else:
        raise TypeError("equations must be a SymPy equality or a sequence of equalities.")

    if not equation_list:
        raise ValueError("At least one equation is required.")
    if any(not isinstance(equation, sp.Equality) for equation in equation_list):
        raise TypeError("Every item in equations must be a SymPy equality.")

    if isinstance(num_solutions, bool) or not isinstance(num_solutions, int):
        raise TypeError("num_solutions must be a positive integer.")
    if num_solutions <= 0:
        raise ValueError("num_solutions must be a positive integer.")

    try:
        candidate_values = np.asarray(list(series), dtype=float)
    except (TypeError, ValueError) as error:
        raise ValueError("series must contain positive numeric values.") from error

    if candidate_values.ndim != 1 or candidate_values.size == 0:
        raise ValueError("series must be a non-empty one-dimensional collection.")
    if not np.all(np.isfinite(candidate_values)) or np.any(candidate_values <= 0):
        raise ValueError("series values must be finite and positive.")
    candidate_values = np.unique(candidate_values)

    variables = sorted(
        set().union(*(equation.free_symbols for equation in equation_list)),
        key=lambda symbol: (symbol.name, sp.srepr(symbol)),
    )
    if not variables:
        raise ValueError("The equations must contain at least one symbol.")

    variable_names = [variable.name for variable in variables]
    if len(set(variable_names)) != len(variable_names):
        raise ValueError("Equation variables must have unique names.")
    if {"Rank", "error"}.intersection(variable_names):
        raise ValueError("Variable names cannot be 'Rank' or 'error'.")

    ranked_solutions: list[tuple[float, tuple[float, ...]]] = []
    for assignment in product(candidate_values, repeat=len(variables)):
        substitutions = dict(zip(variables, assignment))
        squared_residuals: list[float] = []

        for equation in equation_list:
            try:
                calculated = float(sp.N(equation.lhs.subs(substitutions)))
                target = float(sp.N(equation.rhs.subs(substitutions)))
            except (TypeError, ValueError, OverflowError, ZeroDivisionError):
                break

            if not np.isfinite(calculated) or not np.isfinite(target) or target == 0.0:
                break

            residual = (calculated - target) / target
            squared_residuals.append(residual * residual)
        else:
            ranked_solutions.append((sum(squared_residuals), assignment))

    if not ranked_solutions:
        raise ValueError(
            "No candidate assignment has finite, non-zero targets for every equation."
        )

    ranked_solutions.sort(key=lambda solution: (solution[0], solution[1]))
    rows = [
        (rank, *assignment, error)
        for rank, (error, assignment) in enumerate(
            ranked_solutions[:num_solutions], start=1
        )
    ]
    return pd.DataFrame(rows, columns=["Rank", *variable_names, "error"])
