# Jmail Client

Easy Python library for the [Jmail Data API](https://jmail.world/docs) - the Jeffrey Epstein email archive.

No API keys. No rate limits. No authentication. Just data.

## Install

```bash
pip install jmail-client
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install jmail-client
```

## Quick Start

```python
from jmail import JmailClient

client = JmailClient()

# All emails with full body text (1.78M emails, ~334 MB)
df = client.emails()

# Network-only view (no body text, ~41 MB)
df = client.emails(slim=True)
print(df.head())

# Documents with full extracted text
docs = client.documents(include_text=True)

# Photos, people, and facial recognition data
photos = client.photos()
people = client.people()
faces = client.photo_faces()

# iMessage conversations and messages
convos = client.imessage_conversations()
messages = client.imessage_messages()

# Crowd-sourced star counts
stars = client.star_counts()

# Release batch metadata
batches = client.release_batches()
```

## CLI

The package includes a command-line tool:

```bash
# First 5 emails, network-only view
jmail emails --slim --head 5

# All documents with full text
jmail documents --include-text

# Print all dataset URLs
jmail urls

# Get manifest with dataset checksums
jmail manifest

# Fresh download (skip cache)
jmail emails --no-cache --head 5

# Print DuckDB SQL examples
jmail duckdb-examples
```

## Datasets

All files are served from `https://data.jmail.world/v1/`.

| Dataset | Method | Records | ~Size |
|---|---|---|---|
| Emails (full) | `client.emails()` | 1.78M | 334 MB |
| Emails (slim) | `client.emails(slim=True)` | 1.78M | 41 MB |
| Documents | `client.documents()` | 1.41M | 25 MB |
| Documents (full text) | `client.documents(include_text=True)` | 1.41M | Large |
| Photos | `client.photos()` | 18K | ~1 MB |
| People | `client.people()` | 473 | <100 KB |
| Photo Faces | `client.photo_faces()` | 975 | <100 KB |
| iMessage Conversations | `client.imessage_conversations()` | 15 | <10 KB |
| iMessage Messages | `client.imessage_messages()` | 4.5K | ~172 KB |
| Star Counts | `client.star_counts()` | 414K | ~2 MB |
| Release Batches | `client.release_batches()` | 11 | <10 KB |

## Caching

The client uses ETag-based conditional requests to avoid re-downloading unchanged files. Cache is stored in `~/.cache/jmail/`.

```python
# Disable caching (always download fresh)
client = JmailClient(cache=False)

# Clear cache
client.clear_cache()
```

## Get Raw URLs

For use with DuckDB, Polars, or other tools:

```python
url = client.url("emails-slim")
# -> "https://data.jmail.world/v1/emails-slim.parquet"

url = client.url("emails-slim", fmt="ndjson.gz")
# -> "https://data.jmail.world/v1/emails-slim.ndjson.gz"

# All URLs
for name, formats in client.urls().items():
    print(name, formats["parquet"])
```

## DuckDB (zero download)

Query Parquet files directly over HTTP without downloading:

```sql
SELECT sender, COUNT(*) AS n
FROM read_parquet('https://data.jmail.world/v1/emails-slim.parquet')
GROUP BY sender ORDER BY n DESC LIMIT 20;
```

## Dependencies

- `pandas` - DataFrame operations
- `pyarrow` - Parquet file reading
- `requests` - HTTP downloads

## License

AGPL-3.0. See [LICENSE](LICENSE).

## Data Sources

All data comes from three primary sources:
- House Oversight Committee releases
- Department of Justice releases
- Yahoo account releases

Data is public domain (US government records). See the [Jmail documentation](https://jmail.world/docs) for full details.
