import pytest
import numpy as np
import pandas as pd

from hydroserverpy.etl.operations.arithmetic_expression import ArithmeticExpressionOperation
from hydroserverpy.etl.exceptions import ETLError


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

def _make_op(expression, target_identifier="target_1"):
    return ArithmeticExpressionOperation(
        type="arithmetic_expression",
        expression=expression,
        target_identifier=target_identifier,
    )


def _make_series(*values):
    return pd.Series(list(values), dtype="float64")


# ---------------------------------------------------------------------------
# Model configuration and expression validation
# ---------------------------------------------------------------------------

class TestArithmeticExpressionOperationModel:

    def test_expression_is_stored(self):
        op = _make_op("x * 2")
        assert op.expression == "x * 2"

    def test_target_identifier_is_stored(self):
        op = _make_op("x * 2", target_identifier="my_target")
        assert op.target_identifier == "my_target"

    def test_expression_is_required(self):
        with pytest.raises(Exception):
            ArithmeticExpressionOperation(type="arithmetic_expression", target_identifier="t")  # noqa

    def test_target_identifier_is_required(self):
        with pytest.raises(Exception):
            ArithmeticExpressionOperation(type="arithmetic_expression", expression="x * 2")  # noqa

    def test_compiled_code_is_stored_on_init(self):
        op = _make_op("x * 2")
        assert op._compiled is not None

    @pytest.mark.parametrize("expression", [
        "x + 1",
        "x - 1",
        "x * 2",
        "x / 2",
        "x * 2 + 1",
        "(x + 1) * 2",
        "-x",
        "+x",
        "x * 0.5",
        "1 + 2",
    ])
    def test_valid_expressions_are_accepted(self, expression):
        op = _make_op(expression)
        assert op is not None

    def test_disallowed_variable_raises_value_error(self):
        with pytest.raises(ValueError, match="'x'"):
            _make_op("y * 2")

    def test_disallowed_variable_error_includes_variable_name(self):
        with pytest.raises(ValueError, match="y"):
            _make_op("y * 2")

    def test_string_literal_raises_value_error(self):
        with pytest.raises(ValueError, match="numeric literals"):
            _make_op("x + 'hello'")

    def test_boolean_literal_raises_value_error(self):
        with pytest.raises(ValueError, match="numeric literals"):
            _make_op("x + True")

    def test_function_call_raises_value_error(self):
        with pytest.raises(ValueError, match="Only"):
            _make_op("abs(x)")

    def test_comparison_operator_raises_value_error(self):
        with pytest.raises(ValueError, match="Only"):
            _make_op("x > 2")

    def test_invalid_syntax_raises_value_error(self):
        with pytest.raises(ValueError, match="Failed to compile"):
            _make_op("x +* 2")

    def test_error_includes_target_identifier(self):
        with pytest.raises(ValueError, match="my_target"):
            _make_op("y * 2", target_identifier="my_target")

    def test_error_includes_expression(self):
        with pytest.raises(ValueError, match=r"y \* 2"):
            _make_op("y * 2")


# ---------------------------------------------------------------------------
# apply
# ---------------------------------------------------------------------------

class TestArithmeticExpressionOperationApply:

    def test_addition(self):
        op = _make_op("x + 1")
        result = op.apply(_make_series(1.0, 2.0, 3.0))
        pd.testing.assert_series_equal(result, _make_series(2.0, 3.0, 4.0))

    def test_subtraction(self):
        op = _make_op("x - 1")
        result = op.apply(_make_series(1.0, 2.0, 3.0))
        pd.testing.assert_series_equal(result, _make_series(0.0, 1.0, 2.0))

    def test_multiplication(self):
        op = _make_op("x * 2")
        result = op.apply(_make_series(1.0, 2.0, 3.0))
        pd.testing.assert_series_equal(result, _make_series(2.0, 4.0, 6.0))

    def test_division(self):
        op = _make_op("x / 2")
        result = op.apply(_make_series(2.0, 4.0, 6.0))
        pd.testing.assert_series_equal(result, _make_series(1.0, 2.0, 3.0))

    def test_compound_expression(self):
        op = _make_op("x * 2 + 1")
        result = op.apply(_make_series(1.0, 2.0, 3.0))
        pd.testing.assert_series_equal(result, _make_series(3.0, 5.0, 7.0))

    def test_parenthesized_expression(self):
        op = _make_op("(x + 1) * 2")
        result = op.apply(_make_series(1.0, 2.0, 3.0))
        pd.testing.assert_series_equal(result, _make_series(4.0, 6.0, 8.0))

    def test_unary_negation(self):
        op = _make_op("-x")
        result = op.apply(_make_series(1.0, -2.0, 3.0))
        pd.testing.assert_series_equal(result, _make_series(-1.0, 2.0, -3.0))

    def test_float_literal(self):
        op = _make_op("x * 0.5")
        result = op.apply(_make_series(2.0, 4.0))
        pd.testing.assert_series_equal(result, _make_series(1.0, 2.0))

    def test_nan_values_propagate(self):
        op = _make_op("x * 2")
        result = op.apply(_make_series(1.0, float("nan"), 3.0))
        assert np.isnan(result.iloc[1])

    def test_division_by_zero_produces_inf(self):
        op = _make_op("x / 0")
        result = op.apply(_make_series(1.0, 2.0))
        assert np.isinf(result.iloc[0])

    def test_returns_series(self):
        op = _make_op("x + 1")
        result = op.apply(_make_series(1.0))
        assert isinstance(result, pd.Series)

    def test_preserves_index(self):
        op = _make_op("x + 1")
        series = pd.Series([1.0, 2.0], index=[10, 20])
        result = op.apply(series)
        assert list(result.index) == [10, 20]

    def test_eval_error_raises_etl_error(self):
        op = _make_op("x + 1")
        with pytest.raises(ETLError, match="Failed to evaluate"):
            op.apply("not a series")  # noqa

    def test_eval_error_includes_target_identifier(self):
        op = _make_op("x + 1", target_identifier="my_target")
        with pytest.raises(ETLError, match="my_target"):
            op.apply("not a series")  # noqa

    def test_eval_error_includes_expression(self):
        op = _make_op("x + 1")
        with pytest.raises(ETLError, match=r"x \+ 1"):
            op.apply("not a series")  # noqa

    def test_eval_error_chains_original_exception(self):
        op = _make_op("x + 1")
        with pytest.raises(ETLError) as exc_info:
            op.apply("not a series")  # noqa
        assert exc_info.value.__cause__ is not None
