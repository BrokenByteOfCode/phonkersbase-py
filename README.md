# PhonkersBase Python Client

A Python client library for interacting with the PhonkersBase API (phonkersbase.com).

## Features

- Search and retrieve artists from PhonkersBase
- Filter artists by label and country
- Built-in caching support
- Pagination helpers
- Type hints support
- Error handling

## Installation

```bash
pip install phonkersbase
```

## Quick Start

```python
from phonkersbase import phonkerbase, ArtistLabel

# Basic usage
artists = phonkerbase.search_artists("phonk")

# Filter by label
approved_artists = phonkerbase.get_artists_by_label(ArtistLabel.APPROVED)

# Filter by country
uk_artists = phonkerbase.get_artists_by_country("uk")

# Paginate through all results
all_artists = phonkerbase.paginate_all_artists(label=ArtistLabel.APPROVED)
```

## API Reference

### PhonkersBaseAPI

The main client class for interacting with the PhonkersBase API.

```python
client = PhonkersBaseAPI(
    timeout=10,  # Request timeout in seconds
    cache_ttl=3600,  # Cache TTL in seconds
    cache_size=2048  # Maximum number of cached items
)
```

### Methods

- `get_artists(search=None, label=None, country=None, limit=25, offset=0, locale='uk')`
- `get_countries()`
- `search_artists(query, **kwargs)`
- `get_artists_by_label(label, **kwargs)`
- `get_artists_by_country(country, **kwargs)`
- `paginate_all_artists(**kwargs)`
- `clear_cache()`
- `get_cache_info()`

### Artist Labels

Available artist labels (via `ArtistLabel` enum):
- BASE
- APPROVED
- UNKNOWN
- PRIDE
- BLOCKED
- WARNING

## Error Handling

The library uses the `PhonkersBaseException` class for error handling:

```python
try:
    artists = phonkerbase.search_artists("archez")
except PhonkersBaseException as e:
    print(f"API Error: {e}")
```

## License

MIT License
