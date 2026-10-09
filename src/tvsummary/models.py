"""The Show record class."""


class Show:
    """One TV show whose values are cleaned when it is created.

    Missing or malformed data is handled here, in one place:
    rating, language and premiere year become None when unusable,
    and genres become an empty set.
    """

    def __init__(self, raw):
        self.id = raw.get("id")
        self.name = str(raw.get("name", "Untitled"))
        self.rating = self._clean_rating(raw.get("rating"))
        self.language = self._clean_language(raw.get("language"))
        self.premiere_year = self._clean_year(raw.get("premiered"))
        self.genres = self._clean_genres(raw.get("genres"))
        self.has_network = bool(raw.get("network") or raw.get("webChannel"))

    @staticmethod
    def _clean_rating(rating):
        """Return the average rating as a float, or None if unusable."""
        if not isinstance(rating, dict):
            return None
        value = rating.get("average")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        if not 0 <= value <= 10:
            return None
        return float(value)

    @staticmethod
    def _clean_language(language):
        """Return the stripped language, or None if missing or blank."""
        if isinstance(language, str) and language.strip():
            return language.strip()
        return None

    @staticmethod
    def _clean_year(premiered):
        """Return the premiere year as an int, or None if malformed."""
        if not isinstance(premiered, str):
            return None
        try:
            year = int(premiered[:4])
        except ValueError:
            return None
        return year if 1850 <= year <= 2100 else None

    @staticmethod
    def _clean_genres(genres):
        """Return the set of clean genre names (empty if none)."""
        if not isinstance(genres, list):
            return set()
        return {g.strip() for g in genres if isinstance(g, str) and g.strip()}

    def __str__(self):
        rating = self.rating if self.rating is not None else "n/a"
        return f"{self.name} (rating: {rating})"