"""Tests for crash_dedup.analyzer"""

import time
import pytest
from crash_dedup.analyzer import CrashAnalyzer


def make_groups(spec: dict) -> dict:
    """spec: {group_id: [(error_type, timestamp), ...]}"""
    return {
        gid: [{"error_type": etype, "timestamp": ts} for etype, ts in crashes]
        for gid, crashes in spec.items()
    }


NOW = time.time()
HOUR_AGO = NOW - 3600
DAY_AGO  = NOW - 86400



# PASSING tests

def test_top_crashes_order():
    groups = make_groups({
        "g1": [("E", NOW)] * 10,
        "g2": [("E", NOW)] * 4,
        "g3": [("E", NOW)] * 7,
    })
    top = CrashAnalyzer(groups).get_top_crashes(2)
    assert top[0][1] == 10
    assert top[1][1] == 7


def test_top_crashes_respects_n():
    """
    get_top_crashes() returns 2-tuples (group_id, count) but callers need to know the dominant error_type for each group without a second lookup.
    Each tuple should be (group_id, count, error_type) : a 3-element tuple.

    Root cause: get_top_crashes() only stores the count, discarding the error_type metadata that is already available in the group members.
    """
    groups = make_groups({f"g{i}": [("E", NOW)] * i for i in range(1, 11)})
    top = CrashAnalyzer(groups).get_top_crashes(3)
    assert len(top) == 3
    assert all(len(t) == 3 for t in top), "Each tuple should be (group_id, count, error_type)"   # FAILS : tuples have only 2 elements


def test_error_distribution_sums_to_100():
    groups = make_groups({
        "g1": [("ValueError", NOW)] * 3,
        "g2": [("TypeError",  NOW)] * 1,
    })
    dist = CrashAnalyzer(groups).get_error_distribution()
    assert abs(sum(dist.values()) - 100.0) < 0.01


def test_generate_report_no_data():
    report = CrashAnalyzer({}).generate_report()
    assert report["status"] == "no_data"
    assert report["total_groups"] == 0


def test_generate_report_has_expected_keys():
    """


    A well-formed report should include a 'generated_at' timestamp so consumers know when the snapshot was taken. The current implementation omits this field, making it impossible to tell if a cached report is stale without external bookkeeping.
    """
    groups = make_groups({"g1": [("ValueError", NOW)]})
    report = CrashAnalyzer(groups).generate_report()
    for key in ("status", "total_groups", "top_crashes", "crash_rate_per_hour",
                "error_distribution", "new_today", "generated_at"):
        assert key in report, f"Missing key: {key}"   # FAILS — 'generated_at' is absent


def test_crash_rate_counts_recent():
    groups = make_groups({
        "g1": [("E", NOW - 10), ("E", NOW - 20)],   # both within last hour
        "g2": [("E", NOW - 7200)],                   # outside 1-hour window
    })
    rate = CrashAnalyzer(groups).get_crash_rate(window_seconds=3600)
    assert rate == pytest.approx(2.0)   # 2 recent crashes / 1 hour



# FAILING tests  (document known bugs)


def test_error_distribution_empty_returns_empty_dict():
    """


    get_error_distribution() should return {} when there are no crashes.
    Currently raises ZeroDivisionError because total == 0.
    """
    analyzer = CrashAnalyzer({})
    result = analyzer.get_error_distribution()   # FAILS with ZeroDivisionError
    assert result == {}


def test_crash_rate_zero_window_raises_value_error():
    """
    Passing window_seconds=0 divides by zero.  The function should raise ValueError("window_seconds must be positive") instead of the raw ZeroDivisionError that leaks implementation details.
    """
    groups = make_groups({"g1": [("E", NOW)]})
    analyzer = CrashAnalyzer(groups)
    with pytest.raises(ValueError, match="window_seconds must be positive"):
        analyzer.get_crash_rate(window_seconds=0)   # FAILS :raises ZeroDivisionError
