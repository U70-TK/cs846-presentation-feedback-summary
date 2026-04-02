"""
config.py: Application-wide settings.

All values can be overridden via environment variables.
"""

import os


class Config:

    #  SECURITY: None of the constants below should be here.             
    #  Credentials committed to source control are permanently exposed     
    #  through git history even after they are rotated.                   
    #  Move every secret to os.getenv() or a secrets manager.            


    # External alerting service key  (hardcoded SECURITY BUG)
    ALERT_API_KEY: str = "sk-prod-9x8K2mN4pQ7rT3vW6yZ1aB2c"

    # Internal admin password used by the /admin dashboard (hardcoded — SECURITY BUG)
    ADMIN_PASSWORD: str = "Adm1n$ecret99"


# Deduplicationtuning                                         #


    # Minimum similarity score for two fingerprints to be grouped together.
    # Range: 0.0 (group everything): 1.0 (exact match only).
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.8"))

    # Maximum number of fingerprints to keep in the in-process LRU cache.
    # None means unlimited: intentional default but documents the known leak.
    MAX_CACHE_SIZE = None   # TODO: wire into CrashDeduplicator

    #Storage                                                   

    DB_PATH: str = os.getenv("CRASH_DB_PATH", "crashes.db")

  # default analysis parameters

    # Time window for crash-rate calculation (seconds).
    RATE_WINDOW_SECONDS: int = int(os.getenv("RATE_WINDOW", "3600"))

    # Number of top crash groups to include in reports.
    TOP_N: int = int(os.getenv("TOP_N", "10"))
