# Epstein Document Search

A searchable database of Epstein court documents using Meilisearch for fast, full-text search capabilities.

## Overview

This project processes court documents related to the Epstein case, extracts metadata (case numbers, page numbers, etc.), and indexes them in Meilisearch for easy searching. It includes a clean web interface for querying the documents.

## Features

- **Full-text search** across all documents
- **Page-level indexing** for precise results
- **Metadata extraction** including case numbers, document IDs, and page numbers
- **Filter by folder** to narrow searches
- **Highlighted search results** showing matching terms
- **Expandable results** to read full document pages

## Project Structure

```
.
├── website/
│   └── index.html          # Web-based search interface
├── prepare_for_meilisearch.py  # Process documents for indexing
├── split_json.py           # Split large JSON files for upload
├── house_dems.pdf          # Sample document
└── house_dems.txt          # Extracted text from sample document
```

Note: The actual document folders (001/, 002/) and generated JSON files are excluded from git due to their size.

## Document Sources

- **Main document folders**: [Google Drive](https://drive.google.com/drive/folders/1TrGxDGQLDLZu1vvvZDBAh-e7wN3y6Hoz) - Contains folders 001/ and 002/ with court documents
- **House Democrats packet**: [Original PDF](https://oversightdemocrats.house.gov/sites/evo-subsites/democrats-oversight.house.gov/files/evo-media-document/packet_redacted_noid.pdf) - Converted to text as `house_dems.txt`

## Requirements

- Python 3.6+
- Meilisearch instance (cloud or self-hosted)
- Modern web browser

## Setup

### 1. Obtain Documents

Download documents from the [Google Drive folder](https://drive.google.com/drive/folders/1TrGxDGQLDLZu1vvvZDBAh-e7wN3y6Hoz) and place the extracted court document `.txt` files in numbered folders (e.g., `001/`, `002/`).

### 2. Process Documents

Run the preparation script to convert documents into Meilisearch-ready JSON:

```bash
python3 prepare_for_meilisearch.py
```

This will:
- Scan all `.txt` files in the directory
- Split documents by page
- Extract metadata (case numbers, page numbers)
- Generate `meilisearch_documents.json`

### 3. Split Large JSON Files (if needed)

If your JSON file is too large for a single upload:

```bash
python3 split_json.py
```

This creates smaller chunks (`meilisearch_documents_part1.json`, etc.).

### 4. Set Up Meilisearch

You can either:

**Option A: Cloud** (Easiest)
- Sign up at [Meilisearch Cloud](https://www.meilisearch.com/cloud)
- Create an index named `epstein`
- Get your API keys

**Option B: Self-Hosted**
- Follow [Meilisearch installation guide](https://www.meilisearch.com/docs/learn/getting_started/installation)
- Run: `./meilisearch --master-key="YOUR_MASTER_KEY"`

### 5. Upload Documents

Use the Meilisearch API or SDK to upload your JSON files:

```bash
curl -X POST 'http://localhost:7700/indexes/epstein/documents' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_ADMIN_API_KEY' \
  --data-binary @meilisearch_documents.json
```

### 6. Configure Meilisearch Settings

Set up searchable and filterable attributes:

```bash
# Searchable attributes
curl -X PUT 'http://localhost:7700/indexes/epstein/settings/searchable-attributes' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_ADMIN_API_KEY' \
  --data '["content", "document_id", "case_number"]'

# Filterable attributes
curl -X PUT 'http://localhost:7700/indexes/epstein/settings/filterable-attributes' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_ADMIN_API_KEY' \
  --data '["folder", "page_number", "case_number"]'
```

### 7. Configure Website

Edit `website/index.html` and update the configuration:

```javascript
const MEILISEARCH_HOST = 'https://your-instance.meilisearch.io';
const MEILISEARCH_API_KEY = 'your-search-api-key'; // Use search-only key, NOT admin key
const INDEX_NAME = 'epstein';
```

**Security Note:** Use a search-only API key (not your admin key) in the website to prevent unauthorized modifications.

### 8. Open Website

Open `website/index.html` in your browser to start searching!

## Document Format

The processing script expects documents with this format:

```
Case 1:19-cv-03377 Document 1-3 Filed 04/16/19 Page 1 of 3
[Document content here...]
```

Each document is split into pages and indexed with:
- `id`: Unique identifier for each page
- `content`: Full text content of the page
- `document_id`: Filename without extension
- `folder`: Source folder (001, 002, etc.)
- `page_number`: Current page number
- `total_pages`: Total pages in document
- `case_number`: Extracted case number
- `source_file`: Relative path to original file

## Usage Tips

- **Exact phrases**: Use quotes for exact phrase matching: `"Jeffrey Epstein"`
- **Folder filtering**: Select a specific folder to narrow results
- **Case numbers**: Search by case number to find all related documents
- **Load more**: Use the "Load More" button to fetch additional results

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is for educational and research purposes. The court documents themselves are public records.

## Acknowledgments

- Built with [Meilisearch](https://www.meilisearch.com) for fast, typo-tolerant search
- Court documents are public records from various legal proceedings
