"""Summarize TV shows from the TVmaze public API.

Downloads one page of show records, cleans them, computes several
aggregations (shows per genre, average rating per language, shows per
decade, top rated shows, data-quality counts) and writes summary.json.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

SOURCE_URL = "https://api.tvmaze.com/shows?page=0"
OUTPUT = Path("summary.json")
TIMEOUT_SECONDS = 10
MIN_RECORDS = 50
UNKNOWN_LANGUAGE = "unknown"
TOP_N = 5


class DownloadError(Exception):
    """Raised when the records cannot be downloaded or understood."""


def fetch_records(url):
    """Download the records from url and return them as a list of dicts.

    Raises DownloadError with a readable message on any network, HTTP or
    JSON problem.
    """
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout as exc:
        raise DownloadError(
            f"The request to {url} timed out after {TIMEOUT_SECONDS} seconds."
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise DownloadError(
            f"Could not connect to {url}. Check your internet connection."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        raise DownloadError(f"The server returned an error: {exc}") from exc
    except (requests.exceptions.RequestException, ValueError) as exc:
        raise DownloadError(f"Could not read the response from {url}: {exc}") from exc

    if not isinstance(data, list):
        raise DownloadError("Unexpected response format: expected a list of shows.")
    return data


def clean_records(raw_records):
    """Keep only usable show records.

    Drops entries that are not dicts, have no id, or repeat an id already
    seen. Returns a tuple (clean_records, skipped_count).
    """
    seen_ids = set()  
    clean = []
    for item in raw_records:
        if not isinstance(item, dict):
            continue
        show_id = item.get("id")
        if show_id is None or show_id in seen_ids:
            continue
        seen_ids.add(show_id)
        clean.append(item)
    return clean, len(raw_records) - len(clean)

def get_rating(show):
    """Return the show's average rating as a float, or None if unusable."""
    rating = show.get("rating")
    if not isinstance(rating, dict):
        return None
    value = rating.get("average")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not 0 <= value <= 10:
        return None
    return float(value)


def get_language(show):
    """Return the show's language, or None if missing or blank."""
    language = show.get("language")
    if isinstance(language, str) and language.strip():
        return language.strip()
    return None


def get_premiere_year(show):
    """Return the premiere year as an int, or None if missing or malformed."""
    premiered = show.get("premiered")
    if not isinstance(premiered, str):
        return None
    try:
        year = int(premiered[:4])
    except ValueError:
        return None
    return year if 1850 <= year <= 2100 else None


def get_genres(show):
    """Return the set of clean genre names for a show (empty if none)."""
    genres = show.get("genres")
    if not isinstance(genres, list):
        return set()
    return {g.strip() for g in genres if isinstance(g, str) and g.strip()}

def shows_per_genre(records):
    """Count shows per genre; a show with several genres counts in each.

    Shows with no genre are not counted here (see count_missing_fields).
    Returns a dict sorted by count, highest first.
    """
    counts = {}
    for show in records:
        for genre in get_genres(show):
            counts[genre] = counts.get(genre, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def average_rating_by_language(records):
    """Return {language: {"average_rating": float, "rated_shows": int}}.

    Shows without a usable rating are skipped, so they cannot drag an
    average toward zero. Shows without a language go under "unknown".
    """
    totals = {}  
    for show in records:
        rating = get_rating(show)
        if rating is None:
            continue
        language = get_language(show) or UNKNOWN_LANGUAGE
        entry = totals.setdefault(language, [0.0, 0])
        entry[0] += rating
        entry[1] += 1
    return {
        language: {
            "average_rating": round(total / count, 2),
            "rated_shows": count,
        }
        for language, (total, count) in sorted(totals.items())
    }


def shows_per_decade(records):
    """Count shows by premiere decade, e.g. {"1990s": 12, "2000s": 30}.

    Shows with a missing or malformed premiere date are left out.
    """
    counts = {}
    for show in records:
        year = get_premiere_year(show)
        if year is None:
            continue
        decade = f"{year // 10 * 10}s"
        counts[decade] = counts.get(decade, 0) + 1
    return dict(sorted(counts.items()))


def top_rated_shows(records, n=TOP_N):
    """Return the n highest-rated shows as a list of {"name", "rating"} dicts."""
    rated = [
        (get_rating(show), str(show.get("name", "Untitled")))
        for show in records
        if get_rating(show) is not None
    ]
    
    rated.sort(key=lambda pair: (-pair[0], pair[1]))
    return [{"name": name, "rating": rating} for rating, name in rated[:n]]


def count_missing_fields(records):
    """Count how many shows lack each field, so gaps are reported openly."""
    return {
        "no_genre": sum(1 for s in records if not get_genres(s)),
        "no_rating": sum(1 for s in records if get_rating(s) is None),
        "no_language": sum(1 for s in records if get_language(s) is None),
        "no_premiere_date": sum(1 for s in records if get_premiere_year(s) is None),
        "no_network_or_web_channel": sum(
            1 for s in records if not s.get("network") and not s.get("webChannel")
        ),
    }


def build_summary(records, skipped_count, url=SOURCE_URL):
    """Combine every aggregation into one dict ready to write as JSON."""
    return {
        "source_url": url,
        "records_processed": len(records),
        "records_skipped": skipped_count,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "shows_per_genre": shows_per_genre(records),
        "average_rating_by_language": average_rating_by_language(records),
        "shows_per_decade": shows_per_decade(records),
        "top_rated_shows": top_rated_shows(records),
        "missing_values": count_missing_fields(records),
    }


def write_summary(summary, path):
    """Write the summary dict to path as UTF-8 JSON with 2-space indent."""
    path = Path(path)
    text = json.dumps(summary, indent=2, ensure_ascii=False)
    path.write_text(text, encoding="utf-8")


def main():
    """Download, clean, summarize and save; exit with a message on failure."""
    try:
        raw_records = fetch_records(SOURCE_URL)
        records, skipped = clean_records(raw_records)
        if len(records) < MIN_RECORDS:
            raise DownloadError(
                f"Only {len(records)} usable records downloaded; "
                f"at least {MIN_RECORDS} are required."
            )
        summary = build_summary(records, skipped)
        write_summary(summary, OUTPUT)
    except DownloadError as exc:
        sys.exit(f"Error: {exc}")
    except OSError as exc:
        sys.exit(f"Error: could not write {OUTPUT}: {exc}")

    print(f"Processed {summary['records_processed']} shows "
          f"({skipped} skipped). Summary written to {OUTPUT}.")


if __name__ == "__main__":
    main()