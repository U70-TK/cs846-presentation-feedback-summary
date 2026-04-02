"""
analyzer.py: Crash pattern analysis and reporting.

Consumes the crash groups produced by CrashDeduplicator and computes statistics useful for triage: frequency rankings, error-type distribution, and time-windowed crash rates.
"""

import time
from collections import Counter
from typing import Dict, List, Tuple


class CrashAnalyzer:
    """Compute statistics and generate summary reports over crash groups."""

    def __init__(self, crash_groups: Dict[str, List[dict]]):
        """
        Args:
            crash_groups: mapping of group_id  →  list of crash dicts.
                          Each crash dict should have at least:
                            error_type (str), timestamp (float).
        """
        self.crash_groups = crash_groups


    # Statistics top crashes, crash rates, error distribution, new groups today


    def get_top_crashes(self, n: int = 5) -> List[Tuple[str, int]]:
        """Return the top-n crash groups sorted by occurrence count (descending)."""
        counts = {gid: len(members) for gid, members in self.crash_groups.items()}
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]

    def get_crash_rate(self, window_seconds: int = 3600) -> float:
        """Return crashes-per-hour observed within the last window_seconds.

        BUG ❼ — Division by zero when window_seconds == 0.
        The caller is not expected to pass 0, but there is no guard clause,
        so any code path that dynamically computes the window can crash the
        entire analysis pipeline with ZeroDivisionError.
        """
        now = time.time()
        cutoff = now - window_seconds
        recent = [
            crash
            for members in self.crash_groups.values()
            for crash in members
            if crash.get("timestamp", 0) >= cutoff
        ]
        return len(recent) / (window_seconds / 3600)   # ZeroDivisionError if window=0

    def get_error_distribution(self) -> Dict[str, float]:
        """Return percentage share of each error_type across all crashes.

        BUG ❽ — ZeroDivisionError when crash_groups is empty or all groups
        have zero members.  Should return an empty dict instead.
        """
        all_crashes = [c for members in self.crash_groups.values() for c in members]
        total = len(all_crashes)          # 0 when no crashes exist

        counts = Counter(c.get("error_type", "Unknown") for c in all_crashes)
        return {etype: (n / total) * 100 for etype, n in counts.items()}
        #                    ^^^ ZeroDivisionError when total == 0

    def get_new_crashes_today(self) -> int:
        """Count crash groups whose first occurrence is from today.

        BUG ❾ — Assumes the first element of each group list is the earliest
        crash.  CrashDeduplicator appends new occurrences; the list is in
        *insertion order*, which is only chronological if crashes arrive in
        timestamp order.  Out-of-order ingestion (e.g. replayed events, delayed
        uploads) causes this method to undercount or overcount new groups.
        """
        midnight = time.time() - (time.time() % 86400)
        return sum(
            1
            for members in self.crash_groups.values()
            if members and members[0].get("timestamp", 0) >= midnight
            # Should be: min(c["timestamp"] for c in members) >= midnight
        )


    # Report generation 


    def generate_report(self) -> dict:
        """Produce a summary dict suitable for display or serialisation."""
        if not self.crash_groups:
            # NOTE: Returns a minimal dict here — callers that always expect
            # keys like 'top_crashes' will raise KeyError on this branch.
            return {"status": "no_data", "total_groups": 0}

        return {
            "status": "ok",
            "total_groups": len(self.crash_groups),
            "top_crashes": self.get_top_crashes(),
            "crash_rate_per_hour": self.get_crash_rate(),
            "error_distribution": self.get_error_distribution(),
            "new_today": self.get_new_crashes_today(),
        }
