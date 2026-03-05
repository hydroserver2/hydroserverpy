import json
import pytest
import pandas as pd
from io import BytesIO, StringIO
from unittest.mock import patch
from jmespath.exceptions import JMESPathError

from hydroserverpy.etl.transformers.base import ETLDataMapping, ETLTargetPath
from hydroserverpy.etl.transformers.json import JSONTransformer
from hydroserverpy.etl.exceptions import ETLError


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

def _make_transformer(**kwargs):
    defaults = dict(timestamp_key="timestamp", jmespath="data")
    defaults.update(kwargs)
    return JSONTransformer(**defaults)


def _make_mapping(source_id, target_id):
    return ETLDataMapping(
        source_identifier=source_id,
        target_paths=[ETLTargetPath(target_identifier=target_id, data_operations=[])],
    )


def _make_payload(data_points, key="data"):
    """Return a JSON string wrapping data_points under the given key."""
    return json.dumps({key: data_points})


def _make_row(timestamp="2024-01-01T00:00:00Z", value=1.0):
    return {"timestamp": timestamp, "value": value}


# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------

class TestJSONTransformerModel:

    def test_jmespath_is_stored(self):
        t = _make_transformer(jmespath="records")
        assert t.jmespath == "records"

    def test_jmespath_is_required(self):
        with pytest.raises(Exception):
            JSONTransformer(timestamp_key="timestamp")  # noqa

    def test_timestamp_key_is_required(self):
        with pytest.raises(Exception):
            JSONTransformer(jmespath="data")  # noqa

    def test_invalid_jmespath_raises_value_error(self):
        with pytest.raises(ValueError, match="invalid JMESPath"):
            _make_transformer(jmespath="[invalid")

    def test_invalid_jmespath_error_includes_expression(self):
        with pytest.raises(ValueError, match=r"\[invalid"):
            _make_transformer(jmespath="[invalid")

    def test_valid_nested_jmespath_accepted(self):
        t = _make_transformer(jmespath="response.data.records")
        assert t.jmespath == "response.data.records"


# ---------------------------------------------------------------------------
# transform – payload type validation
# ---------------------------------------------------------------------------

class TestJSONTransformerPayloadTypeValidation:

    def test_invalid_payload_type_raises_etl_error(self):
        t = _make_transformer()
        with pytest.raises(ETLError, match="payload object of type"):
            t.transform(12345, [_make_mapping("value", "target_1")])  # noqa

    def test_invalid_payload_type_error_includes_type_name(self):
        t = _make_transformer()
        with pytest.raises(ETLError, match="int"):
            t.transform(12345, [_make_mapping("value", "target_1")])  # noqa

    def test_str_payload_is_accepted(self):
        t = _make_transformer()
        result = t.transform(
            _make_payload([_make_row()]),
            [_make_mapping("value", "target_1")],
        )
        assert not result.empty

    def test_bytes_payload_is_accepted(self):
        t = _make_transformer()
        result = t.transform(
            _make_payload([_make_row()]).encode(),  # noqa
            [_make_mapping("value", "target_1")],
        )
        assert not result.empty

    def test_bytesio_payload_is_accepted(self):
        t = _make_transformer()
        result = t.transform(
            BytesIO(_make_payload([_make_row()]).encode()),
            [_make_mapping("value", "target_1")],
        )
        assert not result.empty

    def test_stringio_payload_is_accepted(self):
        t = _make_transformer()
        result = t.transform(
            StringIO(_make_payload([_make_row()])),
            [_make_mapping("value", "target_1")],
        )
        assert not result.empty


# ---------------------------------------------------------------------------
# transform – JSON parsing
# ---------------------------------------------------------------------------

class TestJSONTransformerParsing:

    def test_invalid_json_raises_etl_error(self):
        t = _make_transformer()
        with pytest.raises(ETLError, match="not valid JSON"):
            t.transform("not json at all", [_make_mapping("value", "target_1")])

    def test_invalid_json_error_chains_decode_error(self):
        t = _make_transformer()
        with pytest.raises(ETLError) as exc_info:
            t.transform("not json at all", [_make_mapping("value", "target_1")])
        assert isinstance(exc_info.value.__cause__, Exception)

    def test_top_level_scalar_raises_etl_error(self):
        t = _make_transformer(jmespath="@")
        with pytest.raises(ETLError, match="dictionary or a list"):
            t.transform("42", [_make_mapping("value", "target_1")])

    def test_top_level_list_is_accepted(self):
        t = _make_transformer(jmespath="@")
        result = t.transform(
            json.dumps([_make_row()]),
            [_make_mapping("value", "target_1")],
        )
        assert not result.empty

    def test_top_level_dict_is_accepted(self):
        t = _make_transformer(jmespath="data")
        result = t.transform(
            _make_payload([_make_row()]),
            [_make_mapping("value", "target_1")],
        )
        assert not result.empty


# ---------------------------------------------------------------------------
# transform – JMESPath evaluation
# ---------------------------------------------------------------------------

class TestJSONTransformerJMESPath:

    def test_jmespath_none_result_raises_etl_error(self):
        t = _make_transformer(jmespath="nonexistent_key")
        with pytest.raises(ETLError, match="did not match anything"):
            t.transform(
                _make_payload([_make_row()]),
                [_make_mapping("value", "target_1")],
            )

    def test_jmespath_evaluation_error_raises_etl_error(self):
        t = _make_transformer()
        with patch("jmespath.search", side_effect=JMESPathError("bad")):
            with pytest.raises(ETLError, match="could not be evaluated"):
                t.transform(
                    _make_payload([_make_row()]),
                    [_make_mapping("value", "target_1")],
                )

    def test_jmespath_evaluation_error_chains_original_exception(self):
        t = _make_transformer()
        original = JMESPathError("bad")
        with patch("jmespath.search", side_effect=original):
            with pytest.raises(ETLError) as exc_info:
                t.transform(
                    _make_payload([_make_row()]),
                    [_make_mapping("value", "target_1")],
                )
        assert exc_info.value.__cause__ is original

    def test_dict_result_is_wrapped_in_list(self):
        t = _make_transformer(jmespath="data[0]")
        payload = json.dumps({"data": [_make_row()]})
        result = t.transform(payload, [_make_mapping("value", "target_1")])
        assert len(result) == 1

    def test_nested_jmespath_expression(self):
        t = _make_transformer(jmespath="response.records")
        payload = json.dumps({"response": {"records": [
            _make_row("2024-01-01T00:00:00Z"),
            _make_row("2024-01-02T00:00:00Z"),
        ]}})
        result = t.transform(payload, [_make_mapping("value", "target_1")])
        assert len(result) == 2


# ---------------------------------------------------------------------------
# transform – output structure
# ---------------------------------------------------------------------------

class TestJSONTransformerOutput:

    def test_returns_dataframe(self):
        t = _make_transformer()
        result = t.transform(
            _make_payload([_make_row()]),
            [_make_mapping("value", "target_1")],
        )
        assert isinstance(result, pd.DataFrame)

    def test_result_contains_timestamp_column(self):
        t = _make_transformer()
        result = t.transform(
            _make_payload([_make_row()]),
            [_make_mapping("value", "target_1")],
        )
        assert "timestamp" in result.columns

    def test_result_contains_target_column(self):
        t = _make_transformer()
        result = t.transform(
            _make_payload([_make_row()]),
            [_make_mapping("value", "target_1")],
        )
        assert "target_1" in result.columns

    def test_result_does_not_contain_source_column(self):
        t = _make_transformer()
        result = t.transform(
            _make_payload([_make_row()]),
            [_make_mapping("value", "target_1")],
        )
        assert "value" not in result.columns

    def test_correct_row_count(self):
        t = _make_transformer()
        rows = [_make_row("2024-01-0{}T00:00:00Z".format(i), float(i)) for i in range(1, 4)]
        result = t.transform(
            _make_payload(rows),
            [_make_mapping("value", "target_1")],
        )
        assert len(result) == 3

    def test_empty_jmespath_result_returns_empty_dataframe(self):
        t = _make_transformer()
        result = t.transform(
            _make_payload([]),
            [_make_mapping("value", "target_1")],
        )
        assert result.empty

    def test_empty_result_dataframe_has_correct_columns(self):
        t = _make_transformer()
        result = t.transform(
            _make_payload([]),
            [_make_mapping("value", "target_1")],
        )
        assert "timestamp" in result.columns

    def test_multiple_mappings_produce_multiple_target_columns(self):
        t = _make_transformer()
        rows = [{"timestamp": "2024-01-01T00:00:00Z", "val_a": 1.0, "val_b": 2.0}]
        result = t.transform(
            _make_payload(rows),
            [
                _make_mapping("val_a", "target_1"),
                _make_mapping("val_b", "target_2"),
            ],
        )
        assert "target_1" in result.columns
        assert "target_2" in result.columns
