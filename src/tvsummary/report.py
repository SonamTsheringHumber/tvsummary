"""Building and writing the summary."""

import json
from datetime import datetime, timezone
from pathlib import Path

from . import config


def build_summary(shows, skipped_count, aggregations, url=config.SOURCE_URL):
    """Combine every aggregation into one dict ready to write as JSON.

    Calls compute() on each object without checking its subclass.
    """
    summary = {
        "source_url": url,
        "records_processed": len(shows),
        "records_skipped": skipped_count,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    for aggregation in aggregations:
        summary[aggregation.name] = aggregation.compute(shows)
    return summary


def write_summary(summary, path=config.OUTPUT_PATH):
    """Write the summary dict to path as UTF-8 JSON with 2-space indent."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(summary, indent=2, ensure_ascii=False)
    path.write_text(text, encoding="utf-8")