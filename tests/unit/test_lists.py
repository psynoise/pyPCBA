"""Unit tests for the preferred-value series utilities."""

import numpy as np

from pyPCBA.lists import e_series


def test_e_series_e12_range() -> None:
    """E12 values should be generated in ascending order for a decade range."""
    values = e_series("E12", 100, 1000)
    expected = np.array([100.0, 120.0, 150.0, 180.0, 220.0, 270.0, 330.0, 390.0, 470.0, 560.0, 680.0, 820.0, 1000.0])

    np.testing.assert_allclose(values, expected)
    assert values.ndim == 1


def test_e_series_supports_si_strings_and_file_output(tmp_path) -> None:
    """SI-input strings should be accepted and the result may be saved to disk."""
    output_path = tmp_path / "e6-values.txt"
    values = e_series("E6", "1k", "10k", filename=str(output_path))
    expected = np.array([1000.0, 1500.0, 2200.0, 3300.0, 4700.0, 6800.0, 10000.0])

    np.testing.assert_allclose(values, expected)
    assert output_path.exists()

    written_values = np.loadtxt(output_path, dtype=float)
    np.testing.assert_allclose(written_values, expected)
