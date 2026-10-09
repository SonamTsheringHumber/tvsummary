"""Getting the data. The only module that imports requests."""

import requests

from . import config
from .models import Show


class DownloadError(Exception):
    """Raised when the records cannot be downloaded or understood."""


class TVMazeSource:
    """Downloads shows from the TVmaze API and returns Show objects."""

    def __init__(self, url=config.SOURCE_URL, timeout=config.TIMEOUT_SECONDS):
        self.url = url
        self.timeout = timeout
        self.skipped_count = 0

    def _download(self):
        """Download the raw JSON list, raising DownloadError on any problem."""
        try:
            response = requests.get(self.url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout as exc:
            raise DownloadError(
                f"The request to {self.url} timed out after {self.timeout} seconds."
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise DownloadError(
                f"Could not connect to {self.url}. Check your internet connection."
            ) from exc
        except requests.exceptions.HTTPError as exc:
            raise DownloadError(f"The server returned an error: {exc}") from exc
        except (requests.exceptions.RequestException, ValueError) as exc:
            raise DownloadError(
                f"Could not read the response from {self.url}: {exc}"
            ) from exc

        if not isinstance(data, list):
            raise DownloadError(
                "Unexpected response format: expected a list of shows."
            )
        return data

    def _to_shows(self, raw_records):
        """Keep usable records (dict, has id, no duplicate id) as Show objects."""
        seen_ids = set()
        shows = []
        for item in raw_records:
            if not isinstance(item, dict):
                continue
            show_id = item.get("id")
            if show_id is None or show_id in seen_ids:
                continue
            seen_ids.add(show_id)
            shows.append(Show(item))
        self.skipped_count = len(raw_records) - len(shows)
        return shows

    def fetch(self):
        """Download and return a list of Show objects."""
        return self._to_shows(self._download())