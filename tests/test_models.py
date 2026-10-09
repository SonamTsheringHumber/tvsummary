import unittest

from tvsummary import Show, ShowsPerGenre, ShowsPerDecade, TopRatedShows


def make_show(**overrides):
    raw = {
        "id": 1,
        "name": "Test Show",
        "language": "English",
        "genres": ["Drama"],
        "premiered": "1994-09-22",
        "rating": {"average": 8.0},
        "network": {"name": "X"},
    }
    raw.update(overrides)
    return Show(raw)


class TestShow(unittest.TestCase):
    def test_bad_rating_becomes_none(self):
        self.assertIsNone(make_show(rating={"average": "abc"}).rating)
        self.assertIsNone(make_show(rating=None).rating)
        self.assertIsNone(make_show(rating={"average": 11}).rating)

    def test_blank_language_becomes_none(self):
        self.assertIsNone(make_show(language="   ").language)

    def test_malformed_premiere_becomes_none(self):
        self.assertIsNone(make_show(premiered="n/a").premiere_year)
        self.assertEqual(make_show().premiere_year, 1994)

    def test_str(self):
        self.assertEqual(str(make_show()), "Test Show (rating: 8.0)")


class TestAggregations(unittest.TestCase):
    def setUp(self):
        self.shows = [
            make_show(id=1, name="A", genres=["Drama", "Crime"],
                      rating={"average": 9.0}),
            make_show(id=2, name="B", genres=["Drama"], premiered="2005-01-01",
                      rating={"average": 7.0}),
        ]

    def test_shows_per_genre(self):
        result = ShowsPerGenre().compute(self.shows)
        self.assertEqual(result, {"Drama": 2, "Crime": 1})

    def test_shows_per_decade(self):
        result = ShowsPerDecade().compute(self.shows)
        self.assertEqual(result, {"1990s": 1, "2000s": 1})

    def test_top_rated_first(self):
        result = TopRatedShows(n=1).compute(self.shows)
        self.assertEqual(result, [{"name": "A", "rating": 9.0}])


if __name__ == "__main__":
    unittest.main()