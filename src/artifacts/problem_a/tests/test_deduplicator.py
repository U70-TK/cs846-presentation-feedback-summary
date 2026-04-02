"""Tests for crash_dedup.deduplicator"""

import pytest
from crash_dedup.deduplicator import CrashDeduplicator


def make_crash(error_type="ValueError", message="bad value",
               trace='  File "app.py", line 1, in main\n    raise ValueError("bad value")',
               timestamp=1_700_000_000.0):
    return {
        "error_type": error_type,
        "error_message": message,
        "stack_trace": trace,
        "timestamp": timestamp,
    }



# PASSING tests


def test_first_crash_creates_group():
    """
  

    When a crash is ingested, the deduplicator should stamp it with a
    'processed_at' timestamp so downstream consumers can distinguish
    ingestion time from the original crash timestamp.

    Root cause: add_crash() only adds '_fingerprint' to the crash dict;
    it never records when the crash was processed.
    """
    d = CrashDeduplicator()
    crash = make_crash()
    gid = d.add_crash(crash)
    assert gid is not None
    assert d.group_count() == 1
    assert "processed_at" in crash, "Crash should be stamped with processing time"   # FAILS: field is never added


def test_identical_crashes_share_group():
    d = CrashDeduplicator()
    g1 = d.add_crash(make_crash())
    g2 = d.add_crash(make_crash())
    assert g1 == g2
    assert d.group_count() == 1


def test_different_error_types_different_groups():
    d = CrashDeduplicator()
    g1 = d.add_crash(make_crash("ValueError", "bad value"))
    g2 = d.add_crash(make_crash("TypeError", "bad type"))
    assert g1 != g2
    assert d.group_count() == 2


def test_stats_deduplicated_increments():
    d = CrashDeduplicator()
    d.add_crash(make_crash())
    d.add_crash(make_crash())
    assert d.get_stats()["deduplicated"] == 1


def test_get_group_returns_correct_members():
    d = CrashDeduplicator()
    gid = d.add_crash(make_crash())
    d.add_crash(make_crash())
    members = d.get_group(gid)
    assert len(members) == 2


def test_multiple_unique_crashes_tracked():
    d = CrashDeduplicator()
    for i in range(5):
        d.add_crash(make_crash(f"Error{i}", f"msg{i}"))
    assert d.group_count() == 5



# FAILING tests  (document known bugs)


def test_cache_size_is_bounded():
    """
    After processing many unique crashes the internal cache should not grow beyond a configured limit (Config.MAX_CACHE_SIZE).
    Root cause: _cache has no eviction policy; it grows without bound, which is a memory leak in long-running processes.
    """
    d = CrashDeduplicator()
    for i in range(500):
        d.add_crash(make_crash("ValueError", f"unique message {i}"))
    # Cache should stay bounded, but currently equals the number of unique fingerprints
    assert len(d._cache) <= 100   # FAILS: cache has 500 entries


def test_similarity_metric_is_meaningful():
    """

    compute_similarity() on two MD5 hashes from unrelated crashes should return a low score (near 0).  The current character-positional comparison of uniform hex strings is not a meaningful metric.

    This test shows that two completely different stack traces can score above the SIMILARITY_THRESHOLD just by chance character overlap.
    """
    d = CrashDeduplicator()
    # Two unrelated crashes: different type, different trace
    crash_a = make_crash("MemoryError", "out of memory",
                         '  File "allocator.py", line 99, in alloc')
    crash_b = make_crash("PermissionError", "access denied",
                         '  File "auth.py", line 7, in check_permission')
    d.add_crash(crash_a)
    d.add_crash(crash_b)
    # Unrelated crashes MUST land in different groups; the broken metric
    # could accidentally merge them
    assert d.group_count() == 2   # may FAIL depending on hash collision
