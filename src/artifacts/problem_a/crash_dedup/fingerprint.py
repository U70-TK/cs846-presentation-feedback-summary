"""
fingerprint.py:Crash fingerprint generation.

Parses a raw stack trace and produces a short hash that uniquely
identifies a crash's *type*, so that repeated occurrences can be
grouped together without storing every duplicate.
"""

import hashlib
import re
from typing import List, Tuple


# How many frames to include when building the fingerprint.
# Intentionally small so the hash is "stable" across minor refactors.
MAX_FRAMES = 3  # NOTE: may miss important context for deep call stacks


class CrashFingerprint:
    """Generates a deterministic fingerprint hash for a single crash event."""

    def __init__(self, stack_trace: str, error_type: str, error_message: str):
        self.stack_trace = stack_trace
        self.error_type = error_type
        self.error_message = error_message
        self._parsed_frames: List[Tuple[str, str, str]] = []

    
    # Public API


    def generate(self) -> str:
        """Return a hex-digest fingerprint for this crash.

        The fingerprint is built from:
          - error type
          - error message   ← BUG: dynamic values (IPs, IDs) make identical
                                    crashes produce different fingerprints
          - top MAX_FRAMES stack frames (file + function only, no line numbers)

        Returns:
            32-character hex string (MD5).  # SECURITY: MD5 is cryptographically
                                             # broken; fine for dedup but misleading
        """
        frames = self.parse_frames()
        top_frames = frames[:MAX_FRAMES]

        # BUG ❶ : raw error_message is included verbatim.
        # Two crashes from different database hosts produce different fingerprints
        # even though they represent the exact same code path and root cause:
        #   "Connection refused: 10.0.0.1:5432"  →  fingerprint A
        #   "Connection refused: 192.168.1.5:5432"  →  fingerprint B
        components = [self.error_type, self.error_message]

        for file_path, line_num, func_name in top_frames:
            # Line number deliberately excluded so minor edits don't split groups.
            components.append(f"{file_path}:{func_name}")

        raw = "|".join(components)
        return hashlib.md5(raw.encode()).hexdigest()  # nosec (non-crypto use)

    def parse_frames(self) -> List[Tuple[str, str, str]]:
        """Extract (file, line, function) tuples from a Python traceback string."""
        pattern = r'File "(.+?)", line (\d+), in (.+)'
        self._parsed_frames = re.findall(pattern, self.stack_trace)
        return self._parsed_frames

    def normalize_message(self, message: str) -> str:
        """Strip numeric tokens from a message to aid grouping.

        BUG ❷ : Normalization is incomplete.  It replaces bare digits but
        misses UUIDs, ISO timestamps, IPv4 addresses, and hex error codes.
        Examples that still vary after normalization:
          "Timeout at 2024-01-15T09:23:11Z"
          "Entity 550e8400-e29b-41d4-a716-446655440000 not found"
          "Error 0x8007001F in kernel call"
        """
        normalized = re.sub(r'\b\d+\b', 'N', message)
        return normalized
