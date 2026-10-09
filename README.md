# tvsummary

Downloads TV show records from the TVmaze API and writes a JSON summary
of shows per genre, ratings per language, shows per decade, top-rated
shows and data-quality counts.

## Data source

https://api.tvmaze.com/shows?page=0. One record represents one TV show.
The first page contains about 240 shows.

## Setup

```
conda env create -f environment.yml
conda activate tvsummary
pip install -r requirements.txt
pip install -e .
```

## Run

```
python main.py
```

## Test

```
python -m unittest discover -s tests
```

## Layout

- `config.py`: URL, timeout, output path and thresholds, so all settings live in one place
- `models.py`: the `Show` class, which cleans its own values when created
- `sources.py`: downloading and filtering records; the only module that uses `requests`
- `aggregations.py`: the `Aggregation` base class and one subclass per summary section
- `report.py`: builds the summary dict and writes `summary.json`
- `main.py`: thin entry point that wires the pieces together and prints messages

## What moved where

| Lab 02 function / constant | Where it lives now |
|---|---|
| SOURCE_URL, OUTPUT, TIMEOUT_SECONDS, MIN_RECORDS, UNKNOWN_LANGUAGE, TOP_N | `config.py` |
| DownloadError | `DownloadError` in `sources.py` |
| fetch_records() | `TVMazeSource._download()` in `sources.py` |
| clean_records() | `TVMazeSource._to_shows()` in `sources.py` |
| get_rating() | `Show._clean_rating()` in `models.py` |
| get_language() | `Show._clean_language()` in `models.py` |
| get_premiere_year() | `Show._clean_year()` in `models.py` |
| get_genres() | `Show._clean_genres()` in `models.py` |
| shows_per_genre() | `ShowsPerGenre.compute()` in `aggregations.py` |
| average_rating_by_language() | `AverageRatingByLanguage.compute()` in `aggregations.py` |
| shows_per_decade() | `ShowsPerDecade.compute()` in `aggregations.py` |
| top_rated_shows() | `TopRatedShows.compute()` in `aggregations.py` |
| count_missing_fields() | `MissingValues.compute()` in `aggregations.py` |
| build_summary() | `build_summary()` in `report.py` |
| write_summary() | `write_summary()` in `report.py` |
| main() | `main()` in `main.py` |

## Design choices

- **Show**: represents one record. It cleans its own values in `__init__`, so
  missing or malformed data is dealt with in one place and every other class
  can trust the values.
- **TVMazeSource**: owns the download and the filtering of unusable records,
  and returns `Show` objects instead of dictionaries. Keeping it separate means
  `requests` is imported in only one module.
- **Aggregation and its five subclasses**: the base class defines `compute()`;
  each subclass overrides it for one summary section. `build_summary()` loops
  over a list of aggregation objects and calls `compute()` without checking
  which subclass each one is. Adding one more aggregation means writing one new
  subclass with a `name` and a `compute()` method and adding it to
  `default_aggregations()`. Nothing else changes.
- **config.py**: the URL, timeout, output path and thresholds are in one place,
  with no absolute paths anywhere.

## Known limitations

- Only the first page (page 0) of the TVmaze shows list is downloaded.
- The whole page is held in memory, which would not scale to very large datasets.
- The tests cover `Show` and three aggregations; Lab 04 will extend them.