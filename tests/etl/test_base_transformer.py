import pytest
import numpy as np
import pandas as pd
from datetime import timezone
from unittest.mock import patch

from hydroserverpy.etl.transformers.base import Transformer, ETLDataMapping, ETLTargetPath
from hydroserverpy.etl.operations.arithmetic_expression import ArithmeticExpressionOperation
from hydroserverpy.etl.exceptions import ETLError


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

def _make_transformer(**kwargs):
    """Instantiate a concrete Transformer subclass for testing."""

    class ConcreteTransformer(Transformer):
        def transform(self, payload, data_mappings, **kwargs):
            pass

    defaults = dict(timestamp_key="timestamp")
    defaults.update(kwargs)
    return ConcreteTransformer(**defaults)


def _make_mapping(source_id, target_id, operations=None):
    target_path = ETLTargetPath(
        target_identifier=target_id,
        data_operations=operations or [],
    )
    return ETLDataMapping(source_identifier=source_id, target_paths=[target_path])


def _make_df(rows=None, columns=None):
    """Build a minimal test DataFrame with a timestamp column."""
    if rows is None:
        rows = [
            {"timestamp": "2024-01-01T00:00:00Z", "value": 1.0},
            {"timestamp": "2024-01-02T00:00:00Z", "value": 2.0},
        ]
    df = pd.DataFrame(rows, columns=columns)
    return df


def _make_expr_op(expression, target_identifier="target_1"):
    """Create a real ArithmeticExpressionOperation for use in ETLTargetPath."""
    return ArithmeticExpressionOperation(
        type="arithmetic_expression",
        expression=expression,
        target_identifier=target_identifier,
    )


# ---------------------------------------------------------------------------
# standardize_dataframe – timestamp handling
# ---------------------------------------------------------------------------

class TestStandardizeDataframeTimestamp:

    def test_renames_timestamp_key_column_to_timestamp(self):
        transformer = _make_transformer(timestamp_key="ts")
        df = pd.DataFrame([{"ts": "2024-01-01T00:00:00Z", "value": 1.0}])
        mapping = _make_mapping("value", "target_1")

        result = transformer.standardize_dataframe(df, [mapping])

        assert "timestamp" in result.columns
        assert "ts" not in result.columns

    def test_missing_timestamp_key_raises_etl_error(self):
        transformer = _make_transformer(timestamp_key="nonexistent")
        df = _make_df()
        mapping = _make_mapping("value", "target_1")

        with pytest.raises(ETLError, match="nonexistent"):
            transformer.standardize_dataframe(df, [mapping])

    def test_missing_timestamp_key_error_includes_column_name(self):
        transformer = _make_transformer(timestamp_key="missing_col")
        df = _make_df()
        mapping = _make_mapping("value", "target_1")

        with pytest.raises(ETLError, match="missing_col"):
            transformer.standardize_dataframe(df, [mapping])

    def test_existing_timestamp_column_not_silently_used_when_key_missing(self):
        """A df that already has a 'timestamp' column should not mask a missing timestamp_key."""
        transformer = _make_transformer(timestamp_key="ts")
        df = pd.DataFrame([{"timestamp": "2024-01-01T00:00:00Z", "value": 1.0}])
        mapping = _make_mapping("value", "target_1")

        with pytest.raises(ETLError, match="ts"):
            transformer.standardize_dataframe(df, [mapping])

    def test_timestamp_column_is_parsed_to_utc(self):
        transformer = _make_transformer(timestamp_key="timestamp")
        df = _make_df()
        mapping = _make_mapping("value", "target_1")

        result = transformer.standardize_dataframe(df, [mapping])

        assert result["timestamp"].dt.tz == timezone.utc

    def test_duplicate_timestamps_are_deduplicated(self):
        transformer = _make_transformer(timestamp_key="timestamp")
        df = pd.DataFrame([
            {"timestamp": "2024-01-01T00:00:00Z", "value": 1.0},
            {"timestamp": "2024-01-01T00:00:00Z", "value": 2.0},
        ])
        mapping = _make_mapping("value", "target_1")

        result = transformer.standardize_dataframe(df, [mapping])

        assert len(result) == 1

    def test_last_duplicate_timestamp_is_kept(self):
        transformer = _make_transformer(timestamp_key="timestamp")
        df = pd.DataFrame([
            {"timestamp": "2024-01-01T00:00:00Z", "value": 1.0},
            {"timestamp": "2024-01-01T00:00:00Z", "value": 2.0},
        ])
        mapping = _make_mapping("value", "target_1")

        result = transformer.standardize_dataframe(df, [mapping])

        assert result["target_1"].iloc[0] == 2.0


# ---------------------------------------------------------------------------
# standardize_dataframe – output structure
# ---------------------------------------------------------------------------

class TestStandardizeDataframeOutput:

    def test_result_contains_timestamp_column(self):
        transformer = _make_transformer()
        df = _make_df()
        mapping = _make_mapping("value", "target_1")

        result = transformer.standardize_dataframe(df, [mapping])

        assert "timestamp" in result.columns

    def test_result_contains_target_column(self):
        transformer = _make_transformer()
        df = _make_df()
        mapping = _make_mapping("value", "target_1")

        result = transformer.standardize_dataframe(df, [mapping])

        assert "target_1" in result.columns

    def test_result_does_not_contain_source_column(self):
        transformer = _make_transformer()
        df = _make_df()
        mapping = _make_mapping("value", "target_1")

        result = transformer.standardize_dataframe(df, [mapping])

        assert "value" not in result.columns

    def test_result_has_correct_row_count(self):
        transformer = _make_transformer()
        df = _make_df()
        mapping = _make_mapping("value", "target_1")

        result = transformer.standardize_dataframe(df, [mapping])

        assert len(result) == 2

    def test_one_to_many_mapping_produces_multiple_target_columns(self):
        transformer = _make_transformer()
        df = _make_df()
        mapping = ETLDataMapping(
            source_identifier="value",
            target_paths=[
                ETLTargetPath(target_identifier="target_1", data_operations=[]),
                ETLTargetPath(target_identifier="target_2", data_operations=[]),
            ]
        )

        result = transformer.standardize_dataframe(df, [mapping])

        assert "target_1" in result.columns
        assert "target_2" in result.columns

    def test_multiple_mappings_produce_multiple_target_columns(self):
        transformer = _make_transformer()
        df = pd.DataFrame([
            {"timestamp": "2024-01-01T00:00:00Z", "val_a": 1.0, "val_b": 10.0},
        ])
        mappings = [
            _make_mapping("val_a", "target_1"),
            _make_mapping("val_b", "target_2"),
        ]

        result = transformer.standardize_dataframe(df, mappings)

        assert "target_1" in result.columns
        assert "target_2" in result.columns

    def test_empty_dataframe_returns_empty_result(self):
        transformer = _make_transformer()
        df = pd.DataFrame(columns=["timestamp", "value"])
        mapping = _make_mapping("value", "target_1")

        result = transformer.standardize_dataframe(df, [mapping])

        assert result.empty


# ---------------------------------------------------------------------------
# resolve_source_column
# ---------------------------------------------------------------------------

class TestResolveSourceColumn:

    def test_resolves_string_column_name(self):
        df = pd.DataFrame({"value": [1.0], "other": [2.0]})

        result = Transformer.resolve_source_column(df, "value")

        assert result == "value"

    def test_resolves_integer_as_positional_index(self):
        df = pd.DataFrame({"a": [1.0], "b": [2.0], "c": [3.0]})

        result = Transformer.resolve_source_column(df, 1)

        assert result == "b"

    def test_integer_label_takes_precedence_over_positional_index(self):
        df = pd.DataFrame({0: [1.0], 1: [2.0], 2: [3.0]})

        result = Transformer.resolve_source_column(df, 1)

        assert result == 1

    def test_missing_string_column_raises_etl_error(self):
        df = pd.DataFrame({"value": [1.0]})

        with pytest.raises(ETLError, match="nonexistent"):
            Transformer.resolve_source_column(df, "nonexistent")

    def test_missing_string_column_error_includes_column_name(self):
        df = pd.DataFrame({"value": [1.0]})

        with pytest.raises(ETLError, match="nonexistent"):
            Transformer.resolve_source_column(df, "nonexistent")

    def test_out_of_range_integer_index_raises_etl_error(self):
        df = pd.DataFrame({"a": [1.0], "b": [2.0]})

        with pytest.raises(ETLError, match="out of range"):
            Transformer.resolve_source_column(df, 99)

    def test_out_of_range_integer_index_error_chains_index_error(self):
        df = pd.DataFrame({"a": [1.0], "b": [2.0]})

        with pytest.raises(ETLError) as exc_info:
            Transformer.resolve_source_column(df, 99)

        assert isinstance(exc_info.value.__cause__, IndexError)

    def test_zero_index_resolves_to_first_column(self):
        df = pd.DataFrame({"first": [1.0], "second": [2.0]})

        result = Transformer.resolve_source_column(df, 0)

        assert result == "first"


# ---------------------------------------------------------------------------
# apply_data_transformations
# ---------------------------------------------------------------------------

class TestApplyDataTransformations:

    def test_returns_series_unchanged_when_no_operations(self):
        series = pd.Series([1.0, 2.0, 3.0])
        path = ETLTargetPath(target_identifier="target_1", data_operations=[])

        result = Transformer.apply_data_transformations(series, path)

        pd.testing.assert_series_equal(result, series)

    def test_coerces_object_dtype_to_numeric(self):
        series = pd.Series(["1.0", "2.0", "3.0"])
        path = ETLTargetPath(target_identifier="target_1", data_operations=[])

        result = Transformer.apply_data_transformations(series, path)

        assert result.dtype != "object"
        assert result.tolist() == [1.0, 2.0, 3.0]

    def test_non_numeric_strings_coerced_to_nan(self):
        series = pd.Series(["1.0", "bad", "3.0"])
        path = ETLTargetPath(target_identifier="target_1", data_operations=[])

        result = Transformer.apply_data_transformations(series, path)

        assert np.isnan(result.iloc[1])

    def test_numeric_dtype_is_not_coerced(self):
        series = pd.Series([1.0, 2.0, 3.0], dtype="float64")
        path = ETLTargetPath(target_identifier="target_1", data_operations=[])

        with patch("hydroserverpy.etl.transformers.base.pd.to_numeric") as mock_coerce:
            Transformer.apply_data_transformations(series, path)

        mock_coerce.assert_not_called()

    def test_operation_apply_is_called(self):
        # Uses identity expression "x" to verify the operation is invoked and its result returned.
        series = pd.Series([1.0, 2.0, 3.0])
        path = ETLTargetPath(
            target_identifier="target_1",
            data_operations=[_make_expr_op("x")],
        )

        result = Transformer.apply_data_transformations(series, path)

        pd.testing.assert_series_equal(result, series)

    def test_operations_are_applied_in_order(self):
        # x * 2 then x + 10 on input 1.0 should give (1*2)+10 = 12.
        # If reversed: (1+10)*2 = 22. The distinct expected values confirm ordering.
        series = pd.Series([1.0])
        path = ETLTargetPath(
            target_identifier="target_1",
            data_operations=[
                _make_expr_op("x * 2"),
                _make_expr_op("x + 10"),
            ],
        )

        result = Transformer.apply_data_transformations(series, path)

        assert result.iloc[0] == pytest.approx(12.0)

    def test_output_of_one_operation_is_input_to_next(self):
        # x * 2 then x * 3 on input 1.0 should give (1*2)*3 = 6.
        # If chaining is broken and both receive the original: (1*3) = 3.
        series = pd.Series([1.0])
        path = ETLTargetPath(
            target_identifier="target_1",
            data_operations=[
                _make_expr_op("x * 2"),
                _make_expr_op("x * 3"),
            ],
        )

        result = Transformer.apply_data_transformations(series, path)

        assert result.iloc[0] == pytest.approx(6.0)
