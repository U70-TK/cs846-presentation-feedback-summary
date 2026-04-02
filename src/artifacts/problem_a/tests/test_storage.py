"""Tests for crash_dedup.storage"""

import os
import tempfile
import pytest
from crash_dedup.storage import CrashStorage


@pytest.fixture
def store():
    """Provide a fresh temporary-file-backed CrashStorage for each test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    s = CrashStorage(path)
    yield s
    s.close()
    os.unlink(path)


def sample_crash(**kwargs):
    base = {
        "error_type": "ValueError",
        "error_message": "bad input",
        "stack_trace": '  File "app.py", line 1, in main',
        "timestamp": 1_700_000_000.0,
        "metadata": {},
    }
    base.update(kwargs)
    return base



# PASSING tests


def test_save_returns_row_id(store):
    row_id = store.save_crash("group_1", sample_crash())
    assert row_id == 1


def test_save_multiple_auto_increments(store):
    id1 = store.save_crash("group_1", sample_crash())
    id2 = store.save_crash("group_1", sample_crash())
    assert id2 == id1 + 1


def test_search_by_error_type_finds_match(store):
    store.save_crash("group_1", sample_crash(error_type="ValueError"))
    results = store.search_by_error_type("ValueError")
    assert len(results) == 1


def test_search_by_error_type_no_match(store):
    store.save_crash("group_1", sample_crash(error_type="ValueError"))
    results = store.search_by_error_type("TypeError")
    assert len(results) == 0


def test_get_crashes_by_group(store):
    store.save_crash("group_1", sample_crash())
    store.save_crash("group_1", sample_crash())
    store.save_crash("group_2", sample_crash(error_type="TypeError"))
    results = store.get_crashes_by_group("group_1")
    assert len(results) == 2


def test_count_by_group(store):
    """


    count_by_group() should raise KeyError when called with a group_id that has never been stored, instead of silently returning 0.  Returning 0 masks bugs where callers pass a stale or misspelled group_id and silently get a false 'empty' result.

    Root cause: the SQL COUNT(*) query always returns a row with value 0 for non-existent groups, and the code does not distinguish 'no group' from 'group with zero crashes'.
    """
    store.save_crash("g1", sample_crash())
    store.save_crash("g1", sample_crash())
    assert store.count_by_group("g1") == 2
    with pytest.raises(KeyError):
        store.count_by_group("nonexistent_group")   # FAILS : returns 0 instead of raising


def test_get_recent_respects_limit(store):
    for _ in range(10):
        store.save_crash("g1", sample_crash())
    assert len(store.get_recent(limit=3)) == 3



# FAILING tests  (document security vulnerabilities)


def test_sql_injection_in_search_is_blocked(store):
    """

    search_by_error_type() is vulnerable to SQL injection.  The payload "' OR '1'='1" makes the WHERE clause always true, returning all rows instead of zero.

    This test asserts that the injection returns no results, it FAILS  because the current implementation does NOT us parameterised queries.

    Fix: replace the f-string with:
        conn.execute("SELECT * FROM crashes WHERE error_type = ?", (error_type,))
    """
    store.save_crash("g1", sample_crash(error_type="ValueError"))
    malicious = "' OR '1'='1"
    results = store.search_by_error_type(malicious)
    assert len(results) == 0   # FAILS : injection returns 1 row


def test_sql_injection_in_get_group_is_blocked(store):
    """

    get_crashes_by_group() has the same SQL-injection vulnerability.
    A crafted group_id can exfiltrate or destroy data.
    """
    store.save_crash("g1", sample_crash())
    malicious_group = "' OR '1'='1"
    results = store.get_crashes_by_group(malicious_group)
    assert len(results) == 0   # FAILS : returns all rows
