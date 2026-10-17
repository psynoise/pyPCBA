"""Preferred-value list utilities for electronic component series.

This module provides the preferred-number series used for component
selection and design exploration.
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Iterable

import numpy as np

__all__ = ["e_series"]

_PREFIX_MULTIPLIERS = {
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "µ": 1e-6,
    "m": 1e-3,
    "k": 1e3,
    "M": 1e6,
    "Meg": 1e6,
}

_SERIES_VALUES = {
    "E3": np.array([1.0, 2.2, 4.7], dtype=float),
    "E6": np.array([1.0, 1.5, 2.2, 3.3, 4.7, 6.8], dtype=float),
    "E12": np.array([1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2], dtype=float),
    "E24": np.array([1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1], dtype=float),
    "E48": np.array([1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54, 1.62, 1.69, 1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49, 2.61, 2.74, 2.87, 3.01, 3.16, 3.32, 3.48, 3.65, 3.83, 4.02, 4.22, 4.42, 4.64, 4.87, 5.11, 5.36, 5.62, 5.90, 6.19, 6.49, 6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53], dtype=float),
    "E48_2": np.array([1.00, 1.10, 1.21, 1.33, 1.47, 1.62, 1.78, 1.96, 2.15, 2.37, 2.61, 2.87, 3.16, 3.48, 3.83, 4.22, 4.64, 5.11, 5.62, 6.19, 6.81, 7.50, 8.25, 9.09], dtype=float),
    "E48_4": np.array([1.00, 1.21, 1.47, 1.78, 2.15, 2.61, 3.16, 3.83, 4.64, 5.62, 6.81, 8.25], dtype=float),
    "E96": np.array([1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76], dtype=float),
    "E192": np.array([1.00, 1.01, 1.02, 1.04, 1.05, 1.06, 1.07, 1.09, 1.10, 1.11, 1.13, 1.14, 1.15, 1.17, 1.18, 1.20, 1.21, 1.23, 1.24, 1.26, 1.27, 1.29, 1.30, 1.32, 1.33, 1.35, 1.37, 1.38, 1.40, 1.42, 1.43, 1.45, 1.47, 1.49, 1.50, 1.52, 1.54, 1.56, 1.58, 1.60, 1.62, 1.64, 1.65, 1.67, 1.69, 1.72, 1.74, 1.76, 1.78, 1.80, 1.82, 1.84, 1.87, 1.89, 1.91, 1.93, 1.96, 1.98, 2.00, 2.03, 2.05, 2.08, 2.10, 2.13, 2.15, 2.18, 2.21, 2.23, 2.26, 2.29, 2.32, 2.34, 2.37, 2.40, 2.43, 2.46, 2.49, 2.52, 2.55, 2.58, 2.61, 2.64, 2.67, 2.71, 2.74, 2.77, 2.80, 2.84, 2.87, 2.91, 2.94, 2.98, 3.01, 3.05, 3.09, 3.12, 3.16, 3.20, 3.24, 3.28, 3.32, 3.36, 3.40, 3.44, 3.48, 3.52, 3.57, 3.61, 3.65, 3.70, 3.74, 3.79, 3.83, 3.88, 3.92, 3.97, 4.02, 4.07, 4.12, 4.17, 4.22, 4.27, 4.32, 4.37, 4.42, 4.48, 4.53, 4.59, 4.64, 4.70, 4.75, 4.81, 4.87, 4.93, 4.99, 5.05, 5.11, 5.17, 5.23, 5.30, 5.36, 5.42, 5.49, 5.56, 5.62, 5.69, 5.76, 5.83, 5.90, 5.97, 6.04, 6.12, 6.19, 6.26, 6.34, 6.42, 6.49, 6.57, 6.65, 6.73, 6.81, 6.90, 6.98, 7.06, 7.15, 7.23, 7.32, 7.41, 7.50, 7.59, 7.68, 7.77, 7.87, 7.96, 8.06, 8.16, 8.25, 8.35, 8.45, 8.56, 8.66, 8.76, 8.87, 8.98, 9.09, 9.20, 9.31, 9.42, 9.53, 9.65, 9.76, 9.88], dtype=float),
}


def _parse_numeric_value(value: float | str) -> float:
    """Convert a numeric value or SI-prefixed string into a float."""
    if isinstance(value, (int, float, np.integer, np.floating)):
        numeric_value = float(value)
        if numeric_value <= 0.0:
            raise ValueError("Value must be positive.")
        return numeric_value

    if not isinstance(value, str):
        raise TypeError("Value must be a positive number or numeric string.")

    text = value.strip().replace(",", "")
    if not text:
        raise ValueError("Value string is empty.")

    match = re.fullmatch(
        r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([A-Za-zµΩ]*)",
        text,
    )
    if match is None:
        raise ValueError(f"Could not parse numeric value: {value!r}")

    numeric_part = float(match.group(1))
    suffix = match.group(2)
    if not suffix:
        if numeric_part <= 0.0:
            raise ValueError("Value must be positive.")
        return numeric_part

    for prefix in ("Meg", "µ", "u", "p", "n", "m", "k", "M"):
        if suffix.startswith(prefix):
            multiplier = _PREFIX_MULTIPLIERS[prefix]
            converted_value = numeric_part * multiplier
            if converted_value <= 0.0:
                raise ValueError("Value must be positive.")
            return converted_value

    return numeric_part


def _normalize_series_name(series: str) -> str:
    """Normalize the preferred-number series name."""
    normalized = series.strip().replace(" ", "").upper()
    if normalized not in _SERIES_VALUES:
        raise ValueError(
            f"Unsupported series {series!r}. Supported values are: "
            + ", ".join(sorted(_SERIES_VALUES.keys()))
        )
    return normalized


def _generate_series_values(series_name: str, min_value: float, max_value: float) -> np.ndarray:
    """Generate preferred values within a range for a given series."""
    bases = _SERIES_VALUES[series_name]
    start_exponent = int(math.floor(math.log10(min_value)))
    end_exponent = int(math.ceil(math.log10(max_value)))

    values: list[float] = []
    for exponent in range(start_exponent, end_exponent + 1):
        decade = 10.0 ** exponent
        for base in bases:
            candidate = base * decade
            if min_value <= candidate <= max_value:
                values.append(float(candidate))

    if not values:
        raise ValueError("No values found in the requested range.")

    unique_values = sorted({float(f"{value:.12g}") for value in values})
    return np.asarray(unique_values, dtype=float)


def e_series(
    series: str,
    min_value: float | str,
    max_value: float | str,
    filename: str | None = None,
) -> np.ndarray:
    """Create a preferred-value series within a numeric range.

    Args:
        series: Preferred-number series identifier. Supported values include
            E3, E6, E12, E24, E48, E48_2, E48_4, E96, and E192.
        min_value: Minimum value to include, expressed as a float or as a string
            with a SI prefix such as ``"1k"`` or ``"4.7u"``.
        max_value: Maximum value to include, expressed as a float or as a string
            with a SI prefix such as ``"10k"`` or ``"2.2M"``.
        filename: Optional file path used to save the generated values as a text
            file. The file extension is normalized to ``.txt``.

    Returns:
        A NumPy array of preferred values sorted in ascending order and limited
        to the specified range.

    Raises:
        ValueError: If the series name is unsupported, the range is invalid,
            or no values are found in the requested range.
        TypeError: If the value type is not numeric or numeric text.

    Example:
        >>> e_series("E12", 100, 100e3)
        array([1.00000000e+02, 1.20000000e+02, 1.50000000e+02, ...])
    """
    normalized_series = _normalize_series_name(series)
    lower_bound = _parse_numeric_value(min_value)
    upper_bound = _parse_numeric_value(max_value)

    if lower_bound >= upper_bound:
        raise ValueError("min_value must be smaller than max_value.")

    values = _generate_series_values(normalized_series, lower_bound, upper_bound)

    if filename is not None:
        output_path = Path(filename)
        if output_path.suffix.lower() != ".txt":
            output_path = output_path.with_suffix(".txt")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        np.savetxt(output_path, values, fmt="%.15g")

    return values
