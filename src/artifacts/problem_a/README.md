# crash-dedup

## Summary

`crash-dedup` is a Python library designed to streamline the management of crash reports in distributed systems. By grouping similar crash reports into a single entry, it reduces alert noise and helps engineers focus on resolving issues efficiently. The library includes features for generating unique fingerprints for stack traces, deduplicating crash data, persisting information in SQLite, and analyzing crash statistics.

## Project layout

```
crash_dedup_project/
├── crash_dedup/
│   ├── __init__.py       # Initializes the crash_dedup module
│   ├── fingerprint.py    # Contains logic for generating unique hashes from stack traces
│   ├── deduplicator.py   # Implements the core logic for grouping similar crash reports
│   ├── storage.py        # Handles SQLite-based persistence for storing crash data
│   ├── analyzer.py       # Provides statistical analysis and reporting tools
│   └── config.py         # Manages application configuration and settings
└── tests/
    ├── test_fingerprint.py  # Unit tests for fingerprinting functionality
    ├── test_deduplicator.py # Unit tests for deduplication logic
    ├── test_storage.py      # Unit tests for storage mechanisms
    └── test_analyzer.py     # Unit tests for analysis and reporting
```

## Quick start

Follow these steps to set up and test the project:

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the test suite to ensure everything is working correctly:

```bash
python -m pytest tests/ -v
```

## Features

- **Crash Deduplication**: Groups similar crash reports to reduce alert noise.
- **Fingerprinting**: Generates unique identifiers for stack traces.
- **Persistence**: Stores crash data using SQLite for reliability.
- **Analysis Tools**: Provides insights and statistics on crash data.

<!-- ## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details. -->
