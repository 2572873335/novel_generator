"""
config_constants.py

This module centralizes all magic numbers and configuration values used within the novel generation process.

Sections:
1. BATCH_CONTROL - Control values related to batch processing
2. CONSISTENCY_CHECK - Values for consistency interval checks
3. QUALITY_GATE - Values relevant to the quality gate checks
4. TIMING - Timing-related constants
5. FILE_PATHS - Standard file paths for chapters, progress, and config files
6. REPORT_CONFIG - Configuration for report formatting
7. IMPORT_RETRY_CONFIG - Patterns for fallback logic during import retries
"""

# BATCH_CONTROL section
DEFAULT_BATCH_SIZE = 20  # Default number of items to process in a batch
MAX_SESSIONS_MULTIPLIER = 2  # Maximum multiplier for session limits

# CONSISTENCY_CHECK section
CHECK_INTERVAL = 5  # Interval in minutes for consistency checks
WINDOW_SIZE = 5  # Size of the window for checks

# QUALITY_GATE section
RETRY_LIMIT = 3  # Maximum number of retries for quality checks

# TIMING section
API_SLEEP_INTERVAL = 0.5  # Time to wait between API calls (in seconds)

# FILE_PATHS section
CHAPTER_FILE = "chapter.txt"  # Standard chapter file name
PROGRESS_FILE = "progress.json"  # Standard progress file name
CONFIG_FILE = "config.yaml"  # Standard configuration file name

# REPORT_CONFIG section
REPORT_TITLE_FORMAT = "Report for {}"  # Formatting for report titles
REPORT_DATE_FORMAT = "%Y-%m-%d"  # Formatting for dates in reports

# IMPORT_RETRY_CONFIG section
FALLBACK_PATTERN = "Try alternative method if {} fails"  # Fallback logic pattern
