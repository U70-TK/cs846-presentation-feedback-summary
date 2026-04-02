"""Tests for crash_dedup.fingerprint"""

import pytest
from crash_dedup.fingerprint import CrashFingerprint


# Fixtures


FULL_TRACE = (
    'Traceback (most recent call last):\n'
    '  File "app/main.py", line 42, in handle_request\n'
    '    result = process(data)\n'
    '  File "app/processor.py", line 17, in process\n'
    '    return parse(raw)\n'
    '  File "app/parser.py", line 8, in parse\n'
    '    raise ValueError("Invalid input")\n'
)

SHORT_TRACE = (
    '  File "app/main.py", line 1, in main\n'
    '    raise RuntimeError("boom")\n'
)


# PASSING tests


def test_generate_returns_32_char_md5():
    fp = CrashFingerprint(FULL_TRACE, "ValueError", "Invalid input")
    assert len(fp.generate()) == 32

def test_generate_is_deterministic():
    fp1 = CrashFingerprint(FULL_TRACE, "ValueError", "Invalid input")
    fp2 = CrashFingerprint(FULL_TRACE, "ValueError", "Invalid input")
    assert fp1.generate() == fp2.generate()

def test_different_error_types_differ():
    fp1 = CrashFingerprint(FULL_TRACE, "ValueError", "msg")
    fp2 = CrashFingerprint(FULL_TRACE, "TypeError", "msg")
    assert fp1.generate() != fp2.generate()

def test_parse_frames_count():
    """


    parse_frames() should return 4-element tuples (file, line, function, module) so that callers can filter by module without parsing the file path themselves.

    Root cause: the regex only captures three groups (file, line, function); it does not extract the top-level module from the file path.
    """
    fp = CrashFingerprint(FULL_TRACE, "ValueError", "Invalid input")
    frames = fp.parse_frames()
    assert len(frames) == 3
    assert all(len(f) == 4 for f in frames), "Each frame should be (file, line, function, module)"   # FAILS — frames have 3 elements

def test_short_trace_does_not_raise():
    fp = CrashFingerprint(SHORT_TRACE, "RuntimeError", "boom")
    result = fp.generate()
    assert result is not None and len(result) == 32

def test_normalize_message_replaces_bare_digits():
    fp = CrashFingerprint("", "", "")
    assert fp.normalize_message("timeout after 30 seconds") == "timeout after N seconds"


# FAILING tests  (document known bugs)


def test_same_crash_different_ip_gets_same_fingerprint():
    """


    Two crashes caused by the same code path but connecting to different database hosts should produce the *same* fingerprint: they are the same bug, just observed on different hosts.

    Root cause: generate() includes the raw error_message in the hash without normalisation, so 'Connection refused: 10.0.0.1' and
    'Connection refused: 192.168.1.5' hash to different values.
    """
    fp1 = CrashFingerprint(FULL_TRACE, "ConnectionError", "Connection refused: 10.0.0.1:5432")
    fp2 = CrashFingerprint(FULL_TRACE, "ConnectionError", "Connection refused: 192.168.1.5:5432")
    assert fp1.generate() == fp2.generate()   # FAILS


def test_normalize_strips_uuid():
    """


    normalize_message() should strip UUIDs so that 'Entity <uuid> not found' errors group together regardless of which entity triggered the crash.

    Root cause: the regex only strips bare decimal integers, not UUID patterns.
    """
    fp = CrashFingerprint("", "", "")
    raw = "Entity 550e8400-e29b-41d4-a716-446655440000 not found"
    normalized = fp.normalize_message(raw)
    assert "550e8400" not in normalized        # FAILS: UUID survives normalisation
