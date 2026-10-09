"""Settings for the tvsummary package. All configuration lives here."""

SOURCE_URL = "https://api.tvmaze.com/shows?page=0"
TIMEOUT_SECONDS = 10
OUTPUT_PATH = "data/processed/summary.json"
MIN_RECORDS = 50
UNKNOWN_LANGUAGE = "unknown"
TOP_N = 5