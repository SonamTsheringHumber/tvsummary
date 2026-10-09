"""Aggregations: a base class and one subclass per summary section."""

from . import config


class Aggregation:
    """Base class. Each subclass sets `name` and overrides compute()."""

    name = "aggregation"

    def compute(self, shows):
        """Return this aggregation's result for a list of Show objects."""
        raise NotImplementedError("Subclasses must override compute().")


class ShowsPerGenre(Aggregation):
    """Count shows per genre, highest count first."""

    name = "shows_per_genre"

    def compute(self, shows):
        counts = {}
        for show in shows:
            for genre in show.genres:
                counts[genre] = counts.get(genre, 0) + 1
        return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


class AverageRatingByLanguage(Aggregation):
    """Average rating and rated-show count per language."""

    name = "average_rating_by_language"

    def compute(self, shows):
        totals = {}
        for show in shows:
            if show.rating is None:
                continue
            language = show.language or config.UNKNOWN_LANGUAGE
            entry = totals.setdefault(language, [0.0, 0])
            entry[0] += show.rating
            entry[1] += 1
        return {
            language: {
                "average_rating": round(total / count, 2),
                "rated_shows": count,
            }
            for language, (total, count) in sorted(totals.items())
        }


class ShowsPerDecade(Aggregation):
    """Count shows by premiere decade, e.g. {"1990s": 12}."""

    name = "shows_per_decade"

    def compute(self, shows):
        counts = {}
        for show in shows:
            if show.premiere_year is None:
                continue
            decade = f"{show.premiere_year // 10 * 10}s"
            counts[decade] = counts.get(decade, 0) + 1
        return dict(sorted(counts.items()))


class TopRatedShows(Aggregation):
    """The n highest-rated shows as {"name", "rating"} dicts."""

    name = "top_rated_shows"

    def __init__(self, n=config.TOP_N):
        self.n = n

    def compute(self, shows):
        rated = [(s.rating, s.name) for s in shows if s.rating is not None]
        rated.sort(key=lambda pair: (-pair[0], pair[1]))
        return [{"name": name, "rating": rating} for rating, name in rated[: self.n]]


class MissingValues(Aggregation):
    """Count how many shows lack each field."""

    name = "missing_values"

    def compute(self, shows):
        return {
            "no_genre": sum(1 for s in shows if not s.genres),
            "no_rating": sum(1 for s in shows if s.rating is None),
            "no_language": sum(1 for s in shows if s.language is None),
            "no_premiere_date": sum(1 for s in shows if s.premiere_year is None),
            "no_network_or_web_channel": sum(1 for s in shows if not s.has_network),
        }


def default_aggregations():
    """Return the aggregations in the same order as the Lab 02 summary."""
    return [
        ShowsPerGenre(),
        AverageRatingByLanguage(),
        ShowsPerDecade(),
        TopRatedShows(),
        MissingValues(),
    ]