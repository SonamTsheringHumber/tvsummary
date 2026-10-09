"""Entry point: wires the pieces together and prints messages."""

import sys

from tvsummary import (
    DownloadError,
    TVMazeSource,
    default_aggregations,
    build_summary,
    write_summary,
    config,
)


def main():
    """Download, summarize and save; exit with a message on failure."""
    source = TVMazeSource()
    try:
        shows = source.fetch()
        if len(shows) < config.MIN_RECORDS:
            raise DownloadError(
                f"Only {len(shows)} usable records downloaded; "
                f"at least {config.MIN_RECORDS} are required."
            )
        summary = build_summary(shows, source.skipped_count, default_aggregations())
        write_summary(summary)
    except DownloadError as exc:
        sys.exit(f"Error: {exc}")
    except OSError as exc:
        sys.exit(f"Error: could not write {config.OUTPUT_PATH}: {exc}")

    print(
        f"Processed {summary['records_processed']} shows "
        f"({source.skipped_count} skipped). Summary written to {config.OUTPUT_PATH}."
    )


if __name__ == "__main__":
    main()