"""Unit tests for symbolic value optimization."""

import numpy as np
import pandas as pd
import pytest
from sympy import Eq, symbols

from pyPCBA.common import eq2sympy
from pyPCBA.values import optimize


def test_optimize_finds_exact_solution_and_returns_expected_columns() -> None:
    """Multiple equations should rank an exact allowed assignment first."""
    r1, r2 = symbols("R1 R2")
    equations = [
        Eq(r2 / (r1 + r2), 0.5),
        Eq(r1 * r2 / (r1 + r2), 50),
    ]

    result = optimize(equations, [10, 50, 100, 200])

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["Rank", "R1", "R2", "error"]
    assert result.iloc[0]["Rank"] == 1
    assert result.iloc[0]["R1"] == 100
    assert result.iloc[0]["R2"] == 100
    assert result.iloc[0]["error"] == pytest.approx(0)


def test_optimize_limits_results_and_sorts_by_relative_least_squares() -> None:
    """Results should be limited to num_solutions and errors should ascend."""
    x, y = symbols("x y")
    result = optimize(Eq(y / (x + y), 0.4), [1, 2, 3, 4], num_solutions=3)

    assert len(result) == 3
    assert result["Rank"].tolist() == [1, 2, 3]
    assert result["error"].is_monotonic_increasing
    assert np.isfinite(result["error"]).all()


def test_optimize_accepts_single_equation_and_allows_equal_values() -> None:
    """A single equation can be passed directly and variables may be equal."""
    x, y = symbols("x y")
    result = optimize(Eq(y / (x + y), 0.5), [10, 20], num_solutions=1)

    assert result.iloc[0]["x"] == result.iloc[0]["y"]
    assert result.iloc[0]["error"] == pytest.approx(0)


def test_eq2sympy_rewrites_divider_and_parallel_operators() -> None:
    """Circuit divider and parallel operators should rewrite to arithmetic forms."""
    r1, r2 = symbols("R1 R2")

    assert eq2sympy("R1 | R2 = 0.33") == Eq(r2 / (r1 + r2), 0.33, evaluate=False)
    assert eq2sympy("R1 // R2 = 50") == Eq((r1 * r2) / (r1 + r2), 50, evaluate=False)


def test_optimize_accepts_equation_strings_with_circuit_operators() -> None:
    """Optimization should convert special-operator strings before SymPy parsing."""
    result = optimize(
        ["R1 | R2 = 0.33", "R1 // R2 = 50"],
        [10, 50, 68, 100, 150],
        num_solutions=5,
    )

    assert list(result.columns) == ["Rank", "R1", "R2", "error"]
    assert result.iloc[0]["error"] >= 0


def test_optimize_rejects_zero_target() -> None:
    """Relative residuals are undefined when the equation target is zero."""
    x = symbols("x")

    with pytest.raises(ValueError, match="No candidate assignment"):
        optimize(Eq(x, 0), [1, 2])


@pytest.mark.parametrize(
    ("equations", "series", "num_solutions", "exception"),
    [
        ([], [1, 2], 10, ValueError),
        (Eq(1, 1, evaluate=False), [1, 2], 10, ValueError),
        (Eq(symbols("x"), 1), [], 10, ValueError),
        (Eq(symbols("x"), 1), [0, 1], 10, ValueError),
        (Eq(symbols("x"), 1), [1, 2], 0, ValueError),
        (["not an equation"], [1, 2], 10, TypeError),
    ],
)
def test_optimize_rejects_invalid_inputs(
    equations: object,
    series: list[float],
    num_solutions: int,
    exception: type[Exception],
) -> None:
    """Invalid equations, candidates, or result counts should fail explicitly."""
    with pytest.raises(exception):
        optimize(equations, series, num_solutions)
