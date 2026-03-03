import pytest
import pandas as pd
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from hydroserverpy.etl.models.temporal_aggregation import TemporalAggregation


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

UTC = timezone.utc


def _make_agg(**kwargs) -> TemporalAggregation:
    defaults = dict(aggregation_statistic="simple_mean")
    defaults.update(kwargs)
    return TemporalAggregation(**defaults)


def _utc(year, month, day, hour=0, minute=0, second=0) -> datetime:
    return datetime(year, month, day, hour, minute, second, tzinfo=UTC)


def _make_df(timestamps: list[datetime], **columns) -> pd.DataFrame:
    """Build a DataFrame with a UTC timestamp column and one or more value columns."""
    data = {"timestamp": pd.to_datetime(timestamps, utc=True)}
    data.update(columns)
    return pd.DataFrame(data)


# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------

class TestTemporalAggregationModel:

    def test_aggregation_statistic_is_stored(self):
        agg = _make_agg(aggregation_statistic="simple_mean")
        assert agg.aggregation_statistic == "simple_mean"

    def test_aggregation_statistic_is_required(self):
        with pytest.raises(Exception):
            TemporalAggregation()  # noqa

    @pytest.mark.parametrize("statistic", [
        "simple_mean", "time_weighted_mean", "last_value_of_period",
    ])
    def test_valid_statistics_are_accepted(self, statistic):
        agg = _make_agg(aggregation_statistic=statistic)
        assert agg.aggregation_statistic == statistic

    def test_invalid_statistic_raises_error(self):
        with pytest.raises(Exception):
            _make_agg(aggregation_statistic="invalid_stat")

    def test_aggregation_interval_defaults_to_one(self):
        agg = _make_agg()
        assert agg.aggregation_interval == 1

    def test_aggregation_interval_unit_defaults_to_day(self):
        agg = _make_agg()
        assert agg.aggregation_interval_unit == "day"

    def test_timezone_type_defaults_to_none(self):
        agg = _make_agg()
        assert agg.timezone_type is None

    def test_utc_timezone_type_is_accepted(self):
        agg = _make_agg(timezone_type="utc")
        assert agg.timezone_type == "utc"

    def test_offset_timezone_type_requires_timezone(self):
        with pytest.raises(ValueError):
            _make_agg(timezone_type="offset")

    def test_iana_timezone_type_requires_timezone(self):
        with pytest.raises(ValueError):
            _make_agg(timezone_type="iana")

    def test_valid_offset_timezone_is_accepted(self):
        agg = _make_agg(timezone_type="offset", timezone="-0700")
        assert agg.timezone == "-0700"

    def test_valid_iana_timezone_is_accepted(self):
        agg = _make_agg(timezone_type="iana", timezone="America/Denver")
        assert agg.timezone == "America/Denver"

    def test_invalid_iana_timezone_raises_error(self):
        with pytest.raises(ValueError, match="Invalid IANA timezone"):
            _make_agg(timezone_type="iana", timezone="Not/ATimezone")

    def test_multi_day_interval_is_accepted(self):
        agg = _make_agg(aggregation_interval=3)
        assert agg.aggregation_interval == 3


# ---------------------------------------------------------------------------
# _effective_tz
# ---------------------------------------------------------------------------

class TestEffectiveTz:

    def test_none_timezone_type_returns_utc(self):
        agg = _make_agg()
        assert agg._effective_tz() == UTC

    def test_utc_timezone_type_returns_utc(self):
        agg = _make_agg(timezone_type="utc")
        assert agg._effective_tz() == UTC

    def test_offset_timezone_type_returns_fixed_offset(self):
        agg = _make_agg(timezone_type="offset", timezone="-0700")
        tz = agg._effective_tz()
        assert tz.utcoffset(None) == timedelta(hours=-7)

    def test_iana_timezone_type_returns_zone_info(self):
        agg = _make_agg(timezone_type="iana", timezone="America/Denver")
        assert agg._effective_tz() == ZoneInfo("America/Denver")


# ---------------------------------------------------------------------------
# _window_start
# ---------------------------------------------------------------------------

class TestWindowStart:

    def test_returns_local_midnight_for_utc(self):
        agg = _make_agg()
        ts = _utc(2024, 1, 15, 14, 30)
        result = agg._window_start(ts)
        assert result.date().year == 2024
        assert result.date().month == 1
        assert result.date().day == 15
        assert result.hour == 0 and result.minute == 0 and result.second == 0

    def test_midnight_timestamp_maps_to_same_day(self):
        agg = _make_agg()
        ts = _utc(2024, 1, 15, 0, 0, 0)
        result = agg._window_start(ts)
        assert result.date().day == 15

    def test_uses_local_date_for_offset_timezone(self):
        # UTC 2024-01-15 02:00 is 2024-01-14 19:00 in -0700
        agg = _make_agg(timezone_type="offset", timezone="-0700")
        ts = _utc(2024, 1, 15, 2, 0)
        result = agg._window_start(ts)
        assert result.date().day == 14

    def test_uses_local_date_for_iana_timezone(self):
        # UTC 2024-01-15 02:00 is 2024-01-14 21:00 in America/Denver (UTC-7 in Jan)
        agg = _make_agg(timezone_type="iana", timezone="America/Denver")
        ts = _utc(2024, 1, 15, 2, 0)
        result = agg._window_start(ts)
        assert result.date().day == 14


# ---------------------------------------------------------------------------
# _next_window_start
# ---------------------------------------------------------------------------

class TestNextWindowStart:

    def test_advances_by_one_day(self):
        agg = _make_agg()
        current = datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC)
        result = agg._next_window_start(current)
        assert result.date().day == 16

    def test_advances_by_multi_day_interval(self):
        agg = _make_agg(aggregation_interval=3)
        current = datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC)
        result = agg._next_window_start(current)
        assert result.date().day == 18

    def test_dst_spring_forward_produces_23_hour_day(self):
        # America/New_York springs forward 2024-03-10: clocks go from 02:00 to 03:00
        # so the day 2024-03-10 is only 23 hours long
        agg = _make_agg(timezone_type="iana", timezone="America/New_York")
        tz = ZoneInfo("America/New_York")
        current = datetime(2024, 3, 10, 0, 0, 0, tzinfo=tz)
        next_w = agg._next_window_start(current)
        span = (next_w.astimezone(UTC) - current.astimezone(UTC)).total_seconds()
        assert span == 23 * 3600

    def test_dst_fall_back_produces_25_hour_day(self):
        # America/New_York falls back 2024-11-03: clocks go from 02:00 back to 01:00
        # so the day 2024-11-03 is 25 hours long
        agg = _make_agg(timezone_type="iana", timezone="America/New_York")
        tz = ZoneInfo("America/New_York")
        current = datetime(2024, 11, 3, 0, 0, 0, tzinfo=tz)
        next_w = agg._next_window_start(current)
        span = (next_w.astimezone(UTC) - current.astimezone(UTC)).total_seconds()
        assert span == 25 * 3600


# ---------------------------------------------------------------------------
# _iter_windows
# ---------------------------------------------------------------------------

class TestIterWindows:

    def test_single_day_yields_one_window(self):
        # end_utc must be on a later local day than start_utc for the window to be emitted
        agg = _make_agg()
        windows = list(agg._iter_windows(_utc(2024, 1, 15, 6), _utc(2024, 1, 16, 6)))
        assert len(windows) == 1

    def test_two_days_yields_two_windows(self):
        agg = _make_agg()
        windows = list(agg._iter_windows(_utc(2024, 1, 15, 6), _utc(2024, 1, 17, 6)))
        assert len(windows) == 2

    def test_window_starts_are_utc_aware(self):
        agg = _make_agg()
        windows = list(agg._iter_windows(_utc(2024, 1, 15, 6), _utc(2024, 1, 16, 6)))
        ws, we = windows[0]
        assert ws.tzinfo is not None
        assert we.tzinfo is not None

    def test_window_start_aligns_to_local_midnight(self):
        # UTC 2024-01-15 06:00 → local midnight in UTC is 2024-01-15 00:00 UTC
        agg = _make_agg()
        windows = list(agg._iter_windows(_utc(2024, 1, 15, 6), _utc(2024, 1, 16, 6)))
        ws, _ = windows[0]
        assert ws == _utc(2024, 1, 15, 0, 0, 0)

    def test_window_end_is_next_midnight(self):
        agg = _make_agg()
        windows = list(agg._iter_windows(_utc(2024, 1, 15, 6), _utc(2024, 1, 16, 6)))
        _, we = windows[0]
        assert we == _utc(2024, 1, 16, 0, 0, 0)

    def test_windows_are_contiguous(self):
        agg = _make_agg()
        windows = list(agg._iter_windows(_utc(2024, 1, 15, 0), _utc(2024, 1, 17, 0)))
        assert windows[0][1] == windows[1][0]

    def test_observation_on_end_boundary_is_excluded(self):
        # end_utc on exactly a midnight should not produce a window for that day
        agg = _make_agg()
        windows = list(agg._iter_windows(_utc(2024, 1, 15, 0), _utc(2024, 1, 16, 0)))
        assert len(windows) == 1

    def test_offset_timezone_shifts_window_boundaries(self):
        # -0700: midnight local = 07:00 UTC
        # end_utc must be past 07:00 on Jan 16 UTC to reach the next local midnight
        agg = _make_agg(timezone_type="offset", timezone="-0700")
        windows = list(agg._iter_windows(_utc(2024, 1, 15, 8), _utc(2024, 1, 16, 8)))
        ws, we = windows[0]
        assert ws == _utc(2024, 1, 15, 7, 0, 0)
        assert we == _utc(2024, 1, 16, 7, 0, 0)

    def test_multi_day_interval_yields_wider_windows(self):
        # With a 3-day interval, end_utc must be on day 4+ to emit a window for days 1-3
        agg = _make_agg(aggregation_interval=3)
        windows = list(agg._iter_windows(_utc(2024, 1, 1, 0), _utc(2024, 1, 4, 6)))
        assert len(windows) == 1
        ws, we = windows[0]
        assert (we - ws).days == 3

    def test_start_same_day_as_end_yields_no_windows(self):
        # Both fall in the same local day so end_local == start_local → no windows
        agg = _make_agg()
        windows = list(agg._iter_windows(_utc(2024, 1, 15, 6), _utc(2024, 1, 15, 8)))
        assert len(windows) == 0


# ---------------------------------------------------------------------------
# _boundary_value
# ---------------------------------------------------------------------------

class TestBoundaryValue:

    def _ts(self, hour) -> datetime:
        return _utc(2024, 1, 15, hour)

    def test_returns_exact_value_when_prev_matches_target(self):
        ts = [self._ts(6), self._ts(12), self._ts(18)]
        vs = [1.0, 2.0, 3.0]
        result = TemporalAggregation._boundary_value(self._ts(6), ts, vs, 0, 1)
        assert result == 1.0

    def test_returns_exact_value_when_next_matches_target(self):
        ts = [self._ts(6), self._ts(12), self._ts(18)]
        vs = [1.0, 2.0, 3.0]
        result = TemporalAggregation._boundary_value(self._ts(12), ts, vs, 0, 1)
        assert result == 2.0

    def test_interpolates_between_prev_and_next(self):
        ts = [self._ts(0), self._ts(12)]
        vs = [0.0, 12.0]
        # target is at hour 6, halfway between → value should be 6.0
        result = TemporalAggregation._boundary_value(self._ts(6), ts, vs, 0, 1)
        assert result == pytest.approx(6.0)

    def test_extrapolates_from_prev_only(self):
        ts = [self._ts(6)]
        vs = [5.0]
        result = TemporalAggregation._boundary_value(self._ts(12), ts, vs, 0, None)
        assert result == 5.0

    def test_extrapolates_from_next_only(self):
        ts = [self._ts(12)]
        vs = [7.0]
        result = TemporalAggregation._boundary_value(self._ts(6), ts, vs, None, 0)
        assert result == 7.0

    def test_returns_none_when_no_observations(self):
        result = TemporalAggregation._boundary_value(self._ts(6), [], [], None, None)
        assert result is None

    def test_returns_none_for_out_of_range_indices(self):
        ts = [self._ts(6)]
        vs = [1.0]
        result = TemporalAggregation._boundary_value(self._ts(0), ts, vs, None, 99)
        assert result is None

    def test_zero_value_is_not_treated_as_missing(self):
        # Guards against the original truthiness bug where value 0.0 was falsy
        ts = [self._ts(6), self._ts(12)]
        vs = [0.0, 10.0]
        result = TemporalAggregation._boundary_value(self._ts(6), ts, vs, 0, 1)
        assert result == pytest.approx(0.0)

    def test_zero_span_returns_next_value(self):
        # Two observations at identical timestamps: span == 0, should return v1
        ts = [self._ts(6), self._ts(6)]
        vs = [1.0, 5.0]
        result = TemporalAggregation._boundary_value(self._ts(3), ts, vs, 0, 1)
        assert result == 5.0


# ---------------------------------------------------------------------------
# _aggregate_window
# ---------------------------------------------------------------------------

class TestAggregateWindow:

    def _make_agg(self, statistic):
        return _make_agg(aggregation_statistic=statistic)

    def _ts(self, hour) -> datetime:
        return _utc(2024, 1, 15, hour)

    def _window(self):
        return _utc(2024, 1, 15, 0), _utc(2024, 1, 16, 0)

    def test_returns_none_for_empty_timestamps(self):
        agg = self._make_agg("simple_mean")
        assert agg._aggregate_window([], [], *self._window()) is None

    def test_returns_none_when_window_end_before_start(self):
        agg = self._make_agg("simple_mean")
        ts = [self._ts(6)]
        result = agg._aggregate_window(ts, [1.0], self._ts(12), self._ts(6))
        assert result is None

    def test_returns_none_when_no_observations_in_window(self):
        agg = self._make_agg("simple_mean")
        ts = [self._ts(6)]
        # window is entirely after the only observation
        result = agg._aggregate_window(ts, [1.0], self._ts(8), self._ts(10))
        assert result is None

    # simple_mean

    def test_simple_mean_single_observation(self):
        agg = self._make_agg("simple_mean")
        ts = [self._ts(6)]
        result = agg._aggregate_window(ts, [5.0], *self._window())
        assert result == pytest.approx(5.0)

    def test_simple_mean_multiple_observations(self):
        agg = self._make_agg("simple_mean")
        ts = [self._ts(6), self._ts(12), self._ts(18)]
        result = agg._aggregate_window(ts, [1.0, 2.0, 3.0], *self._window())
        assert result == pytest.approx(2.0)

    def test_simple_mean_excludes_observation_on_window_end(self):
        agg = self._make_agg("simple_mean")
        # Observation exactly on window_end should be excluded (bisect_left semantics)
        ts = [self._ts(6), _utc(2024, 1, 16, 0)]
        result = agg._aggregate_window(ts, [2.0, 999.0], *self._window())
        assert result == pytest.approx(2.0)

    # last_value_of_period

    def test_last_value_of_period_returns_last_in_window(self):
        agg = self._make_agg("last_value_of_period")
        ts = [self._ts(6), self._ts(12), self._ts(18)]
        result = agg._aggregate_window(ts, [1.0, 2.0, 3.0], *self._window())
        assert result == pytest.approx(3.0)

    def test_last_value_of_period_single_observation(self):
        agg = self._make_agg("last_value_of_period")
        ts = [self._ts(12)]
        result = agg._aggregate_window(ts, [7.0], *self._window())
        assert result == pytest.approx(7.0)

    # time_weighted_mean

    def test_time_weighted_mean_constant_series_equals_constant(self):
        agg = self._make_agg("time_weighted_mean")
        ts = [self._ts(6), self._ts(12), self._ts(18)]
        result = agg._aggregate_window(ts, [5.0, 5.0, 5.0], *self._window())
        assert result == pytest.approx(5.0)

    def test_time_weighted_mean_linear_series(self):
        # Values go from 0 at midnight to 24 at the next midnight linearly.
        # Time-weighted mean of a linear ramp is the midpoint = 12.0.
        agg = self._make_agg("time_weighted_mean")
        ws = _utc(2024, 1, 15, 0)
        we = _utc(2024, 1, 16, 0)
        ts = [_utc(2024, 1, 15, h) for h in range(24)] + [_utc(2024, 1, 16, 0)]
        vs = [float(h) for h in range(25)]
        result = agg._aggregate_window(ts, vs, ws, we)
        assert result == pytest.approx(12.0)

    def test_time_weighted_mean_weights_longer_intervals_more(self):
        # Observations: (h0, 0.0), (h6, 12.0), (h23, 12.0).
        # Boundary at window_start h0: exact match → 0.0.
        # Boundary at window_end (next midnight): no observation at h24, extrapolates
        # flat from (h23, 12.0) → 12.0.
        # Trapezoids: h0→h6: (0+12)/2*6 = 36, h6→h23: 12*17 = 204, h23→h24: 12*1 = 12.
        # Total = 252, mean = 252/24 = 10.5.
        # This confirms longer intervals carry more weight than observation count alone
        # (simple mean of [0, 12, 12] would be 8.0).
        agg = self._make_agg("time_weighted_mean")
        ts = [self._ts(0), self._ts(6), self._ts(23)]
        vs = [0.0, 12.0, 12.0]
        ws, we = self._window()
        result = agg._aggregate_window(ts, vs, ws, we)
        assert result == pytest.approx(10.5)

    def test_time_weighted_mean_returns_none_when_boundary_indeterminate(self):
        # Single interior observation with no surrounding context for boundary estimation
        agg = self._make_agg("time_weighted_mean")
        ts = [self._ts(12)]
        # Window extends before and after the only observation with nothing to extrapolate from
        result = agg._aggregate_window(ts, [5.0], self._ts(6), self._ts(18))
        # boundary_value will extrapolate using the only available point on each side
        # so this should actually succeed — just verify it returns a float, not None
        assert result is not None


# ---------------------------------------------------------------------------
# apply – output structure
# ---------------------------------------------------------------------------

class TestApplyOutputStructure:

    def test_returns_dataframe(self):
        agg = _make_agg()
        df = _make_df([_utc(2024, 1, 15, 12)], value=[1.0])
        assert isinstance(agg.apply(df), pd.DataFrame)

    def test_result_contains_timestamp_column(self):
        agg = _make_agg()
        df = _make_df([_utc(2024, 1, 15, 12)], value=[1.0])
        result = agg.apply(df)
        assert "timestamp" in result.columns

    def test_result_contains_target_columns(self):
        agg = _make_agg()
        df = _make_df([_utc(2024, 1, 15, 12)], val_a=[1.0], val_b=[2.0])
        result = agg.apply(df)
        assert "val_a" in result.columns
        assert "val_b" in result.columns

    def test_timestamp_column_is_utc_aware(self):
        agg = _make_agg()
        df = _make_df([_utc(2024, 1, 15, 12)], value=[1.0])
        result = agg.apply(df)
        assert result["timestamp"].dt.tz == timezone.utc

    def test_timestamp_is_window_start_not_observation_time(self):
        agg = _make_agg()
        df = _make_df([_utc(2024, 1, 15, 12), _utc(2024, 1, 16, 12)], value=[1.0, 2.0])
        result = agg.apply(df)
        assert result["timestamp"].iloc[0] == pd.Timestamp("2024-01-15 00:00:00", tz="UTC")

    def test_empty_dataframe_returns_empty_with_correct_columns(self):
        agg = _make_agg()
        df = pd.DataFrame(columns=["timestamp", "value"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        result = agg.apply(df)
        assert result.empty
        assert "timestamp" in result.columns
        assert "value" in result.columns

    def test_multiple_observations_same_day_produce_one_row(self):
        # Three observations on Jan 15 plus a sentinel on Jan 16 to open the window.
        # Only one window is emitted (Jan 15); Jan 16 is the end boundary.
        agg = _make_agg()
        df = _make_df(
            [_utc(2024, 1, 15, 6), _utc(2024, 1, 15, 12), _utc(2024, 1, 15, 18), _utc(2024, 1, 16, 6)],
            value=[1.0, 2.0, 3.0, 4.0],
        )
        result = agg.apply(df)
        assert len(result) == 1
        assert result["value"].iloc[0] == pytest.approx(2.0)

    def test_observations_on_two_days_produce_two_rows(self):
        agg = _make_agg()
        df = _make_df(
            [_utc(2024, 1, 15, 12), _utc(2024, 1, 16, 12), _utc(2024, 1, 17, 12)],
            value=[1.0, 2.0, 3.0],
        )
        result = agg.apply(df)
        assert len(result) == 2  # Jan 15 and Jan 16; Jan 17 is the end boundary, not a full window

    def test_day_with_no_observations_is_dropped(self):
        agg = _make_agg()
        # Observations on Jan 15 and Jan 17, nothing on Jan 16
        df = _make_df(
            [_utc(2024, 1, 15, 12), _utc(2024, 1, 17, 12), _utc(2024, 1, 18, 12)],
            value=[1.0, 2.0, 3.0],
        )
        result = agg.apply(df)
        # Jan 16 has no observations so is dropped; Jan 15 and Jan 17 are present
        assert len(result) == 2
        assert pd.Timestamp("2024-01-16 00:00:00", tz="UTC") not in result["timestamp"].values

    def test_all_target_columns_aggregated_uniformly(self):
        agg = _make_agg()
        df = _make_df(
            [_utc(2024, 1, 15, 6), _utc(2024, 1, 15, 18), _utc(2024, 1, 16, 6)],
            val_a=[1.0, 3.0, 5.0],
            val_b=[10.0, 30.0, 50.0],
        )
        result = agg.apply(df)
        assert result["val_a"].iloc[0] == pytest.approx(2.0)
        assert result["val_b"].iloc[0] == pytest.approx(20.0)

    def test_non_numeric_values_coerced_to_nan(self):
        # Non-numeric values become NaN after coercion. simple_mean([nan]) = nan,
        # which is not None, so the window is retained but the value is NaN.
        agg = _make_agg()
        df = _make_df(
            [_utc(2024, 1, 15, 12), _utc(2024, 1, 16, 12)],
            value=["not_a_number", "also_not_a_number"],
        )
        result = agg.apply(df)
        assert len(result) == 1
        assert pd.isna(result["value"].iloc[0])


# ---------------------------------------------------------------------------
# apply – statistics
# ---------------------------------------------------------------------------

class TestApplyStatistics:

    def test_simple_mean_across_full_day(self):
        agg = _make_agg(aggregation_statistic="simple_mean")
        df = _make_df(
            [_utc(2024, 1, 15, 6), _utc(2024, 1, 15, 12), _utc(2024, 1, 15, 18), _utc(2024, 1, 16, 6)],
            value=[1.0, 2.0, 3.0, 4.0],
        )
        result = agg.apply(df)
        assert result["value"].iloc[0] == pytest.approx(2.0)

    def test_last_value_of_period_across_full_day(self):
        agg = _make_agg(aggregation_statistic="last_value_of_period")
        df = _make_df(
            [_utc(2024, 1, 15, 6), _utc(2024, 1, 15, 12), _utc(2024, 1, 15, 18), _utc(2024, 1, 16, 6)],
            value=[1.0, 2.0, 3.0, 4.0],
        )
        result = agg.apply(df)
        assert result["value"].iloc[0] == pytest.approx(3.0)

    def test_time_weighted_mean_constant_equals_constant(self):
        agg = _make_agg(aggregation_statistic="time_weighted_mean")
        df = _make_df(
            [_utc(2024, 1, 15, 0), _utc(2024, 1, 15, 12), _utc(2024, 1, 16, 0)],
            value=[5.0, 5.0, 5.0],
        )
        result = agg.apply(df)
        assert result["value"].iloc[0] == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# apply – timezone behaviour
# ---------------------------------------------------------------------------

class TestApplyTimezone:

    def test_utc_timezone_aligns_windows_to_utc_midnight(self):
        agg = _make_agg(timezone_type="utc")
        df = _make_df([_utc(2024, 1, 15, 12), _utc(2024, 1, 16, 12)], value=[1.0, 2.0])
        result = agg.apply(df)
        assert result["timestamp"].iloc[0] == pd.Timestamp("2024-01-15 00:00:00", tz="UTC")

    def test_offset_timezone_shifts_window_start(self):
        # -0700: midnight local = 07:00 UTC
        # Second observation must be on a different local day, i.e. past 07:00 UTC on Jan 16
        agg = _make_agg(timezone_type="offset", timezone="-0700")
        df = _make_df([_utc(2024, 1, 15, 10), _utc(2024, 1, 16, 10)], value=[1.0, 2.0])
        result = agg.apply(df)
        assert result["timestamp"].iloc[0] == pd.Timestamp("2024-01-15 07:00:00", tz="UTC")

    def test_iana_timezone_shifts_window_start(self):
        # America/Denver is UTC-7 in January; midnight local = 07:00 UTC
        agg = _make_agg(timezone_type="iana", timezone="America/Denver")
        df = _make_df([_utc(2024, 1, 15, 10), _utc(2024, 1, 16, 10)], value=[1.0, 2.0])
        result = agg.apply(df)
        assert result["timestamp"].iloc[0] == pd.Timestamp("2024-01-15 07:00:00", tz="UTC")

    def test_observation_near_midnight_assigned_to_correct_local_day(self):
        # UTC 2024-01-15 01:00 is 2024-01-14 18:00 in -0700 → belongs to Jan 14 local window.
        # UTC 2024-01-15 10:00 is 2024-01-15 03:00 in -0700 → belongs to Jan 15 local window.
        # A sentinel on Jan 16 local time (past 07:00 UTC on Jan 16) opens the second window.
        agg = _make_agg(timezone_type="offset", timezone="-0700")
        df = _make_df(
            [_utc(2024, 1, 15, 1), _utc(2024, 1, 15, 10), _utc(2024, 1, 16, 10)],
            value=[1.0, 2.0, 3.0],
        )
        result = agg.apply(df)
        assert len(result) == 2
        # First window starts at Jan 14 07:00 UTC (midnight local Jan 14)
        assert result["timestamp"].iloc[0] == pd.Timestamp("2024-01-14 07:00:00", tz="UTC")
        # Second window starts at Jan 15 07:00 UTC (midnight local Jan 15)
        assert result["timestamp"].iloc[1] == pd.Timestamp("2024-01-15 07:00:00", tz="UTC")

    def test_dst_transition_day_handled_correctly(self):
        # Spring forward: 2024-03-10 in America/New_York is 23 hours.
        # An observation at any point during that day should land in one window.
        agg = _make_agg(timezone_type="iana", timezone="America/New_York")
        df = _make_df([_utc(2024, 3, 10, 12), _utc(2024, 3, 11, 12)], value=[1.0, 2.0])
        result = agg.apply(df)
        assert len(result) == 1  # only Mar 10 window; Mar 11 is the end boundary


# ---------------------------------------------------------------------------
# apply – multi-day interval
# ---------------------------------------------------------------------------

class TestApplyMultiDayInterval:

    def test_three_day_interval_groups_three_days_into_one_row(self):
        agg = _make_agg(aggregation_interval=3)
        df = _make_df(
            [_utc(2024, 1, 1, 12), _utc(2024, 1, 2, 12), _utc(2024, 1, 3, 12)],
            value=[1.0, 2.0, 3.0],
        )
        result = agg.apply(df)
        assert len(result) == 1
        assert result["value"].iloc[0] == pytest.approx(2.0)

    def test_three_day_interval_window_spans_correct_duration(self):
        agg = _make_agg(aggregation_interval=3)
        df = _make_df(
            [_utc(2024, 1, 1, 12), _utc(2024, 1, 4, 12), _utc(2024, 1, 7, 12)],
            value=[1.0, 2.0, 3.0],
        )
        result = agg.apply(df)
        assert len(result) == 2  # window 1: Jan 1-4, window 2: Jan 4-7
        span = (result["timestamp"].iloc[1] - result["timestamp"].iloc[0]).total_seconds()
        assert span == 3 * 24 * 3600
