"""tvsummary: download TV shows from TVmaze and summarize them."""

from . import config
from .models import Show
from .sources import TVMazeSource, DownloadError
from .aggregations import (
    Aggregation,
    ShowsPerGenre,
    AverageRatingByLanguage,
    ShowsPerDecade,
    TopRatedShows,
    MissingValues,
    default_aggregations,
)
from .report import build_summary, write_summary

__all__ = [
    "config",
    "Show",
    "TVMazeSource",
    "DownloadError",
    "Aggregation",
    "ShowsPerGenre",
    "AverageRatingByLanguage",
    "ShowsPerDecade",
    "TopRatedShows",
    "MissingValues",
    "default_aggregations",
    "build_summary",
    "write_summary",
]