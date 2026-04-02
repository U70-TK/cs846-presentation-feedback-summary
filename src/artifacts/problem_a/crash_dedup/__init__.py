"""
crash_dedup - Crash Report Deduplication System

Groups incoming crash reports by similarity so engineering teams
can triage unique issues instead of reviewing every duplicate.
"""

from .fingerprint import CrashFingerprint
from .deduplicator import CrashDeduplicator
from .storage import CrashStorage
from .analyzer import CrashAnalyzer

__version__ = "0.2.1"
__all__ = ["CrashFingerprint", "CrashDeduplicator", "CrashStorage", "CrashAnalyzer"]
