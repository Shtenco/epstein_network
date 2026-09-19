# Network Risk Analysis: Knowledge Graph Dashboard

Built by an actuary, this is an exposure mapping engine—not a political project. It visualizes hidden network dependencies across messy unstructured records using NER and co-mention analysis, with real document evidence embedded in tooltips. The same logic applies directly to insurance and claims risk management.

**👉 [View the Interactive Dashboard](./GRAPHISTRY_DASHBOARD.html)** | [Educational Guide](./KNOWLEDGE_GRAPH_GUIDE.md)

## 🎯 Overview

This project constructs a **105-node network graph** demonstrating how knowledge graphs surface hidden systemic risks—crucial for insurance underwriting, fraud detection, and counterparty exposure analysis.

**Key Statistics:**
- 105 nodes across 13 professional categories
- 587 edges from document co-mentions  
- 25,793 documents indexed for evidence
- 5 pre-filtered views (Academia, Finance, Entertainment, Israeli Officials, Full Network)

## Why an Actuary built this

This is not a political project. It is an **exposure mapping engine**.

The same logic applies directly to insurance and risk operations: when names, entities, and events are spread across messy, unstructured records, hidden dependencies are easy to miss.

If a Risk Manager recognizes this pattern, they can apply the same approach to their own "black box" of claims data to surface concentration, contagion, and reputational spillover risk earlier.

## 📊 Why This Matters for Risk Management

Network visualization reveals what traditional analysis misses:

| Risk Type | Graph Insight | Insurance Application |
|-----------|---------------|----------------------|
| **Exposure Mapping** | Who's connected across sectors? | Counterparty concentration |
| **Contagion Risk** | Which nodes amplify instability? | Cascade loss modeling |
| **Reputation Cascade** | How do actions ripple through networks? | Reputational risk spillover |
| **Influence Concentration** | Which nodes control information flow? | Fraud detection/PEP screening |
| **Sovereign Risk** | Geopolitical network fragility? | Political risk premiums |

## 🚀 Quick Start

**No installation required:**
1. Open [GRAPHISTRY_DASHBOARD.html](./GRAPHISTRY_DASHBOARD.html) in your browser
2. Click tabs to switch between views
3. Hover over nodes to see roles, connections, and document evidence
4. Zoom/pan to explore subgraphs

**For technical details:**
- See [KNOWLEDGE_GRAPH_GUIDE.md](./KNOWLEDGE_GRAPH_GUIDE.md) for the 5-view insurance analysis
- See [Data Source](#data-source) for methodology

## 📂 What's Included

| File | Purpose |
|------|---------|
| **GRAPHISTRY_DASHBOARD.html** | Interactive 5-view dashboard (self-contained) |
| **KNOWLEDGE_GRAPH_GUIDE.md** | Educational breakdown with insurance principles |
| **plot_receipts.py** | Python pipeline for graph generation |
| **/cache/** | Cached data: parquet, document texts |

## 🔧 Technical Details

**Pipeline (plot_receipts.py):**
1. Stream 2.1M rows from HuggingFace parquet
2. Extract entities via spaCy NER
3. Build co-mention edges (same document = connected)
4. Apply role classification (~60 curated names)
5. Generate 5 pre-filtered Graphistry datasets
6. Embed iframes in HTML dashboard

**Data Quality Controls:**
- Garbage NER filtered (dates, common names, aliases)
- Non-target documents blocklisted (memoir fragments, academic book excerpts)
- Minimum degree threshold (≥2 edges)
- Gossip-network filtering (prevents spurious clusters)

## 📡 Data Source

**[teyler/epstein-files-20k](https://huggingface.co/datasets/teyler/epstein-files-20k)** on HuggingFace:
- 2,136,420 rows from 16,616 unique documents
- DOJ declassifications + FBI/House Oversight releases
- OCR'd text with entity-document co-occurrence relationships

Entity resolution pipeline uses **9 behavioral signals** (name similarity, co-occurrence patterns, location, role consistency) to unify aliases and OCR variants into canonical entities.

## Pipeline overview

```
┌──────────────┐     ┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│   INGEST     │────▶│  CANDIDATE   │────▶│    SCORE      │────▶│   CLUSTER    │
│              │     │  GENERATION  │     │  (9 signals)  │     │ (Union-Find) │
│ HF stream →  │     │              │     │               │     │              │
│ spaCy NER →  │     │ token block  │     │ name sim      │     │ auto-merge   │
│ phonebook →  │     │ abbrev match │     │ edit distance │     │ review queue │
│ mentions     │     │ semantic kNN │     │ last-name sim │     │ resolved     │
│              │     │              │     │ co-occurrence │     │ entities     │
│              │     │              │     │ companions    │     │              │
│              │     │              │     │ location      │     ├──────────────┤
│              │     │              │     │ role, temporal│     │              │
│              │     │              │     └───────┬───────┘     │  RELATION    │
│              │     │              │             │             │  EXTRACTION  │
│              │     │              │     ┌───────▼───────┐     │  (regex)     │
│              │     │              │     │   OPTIMISE    │     │              │
│              │     │              │     │ weights from  │     ├──────────────┤
│              │     │              │     │ gold labels   │     │              │
│              │     │              │     │ (Nelder-Mead) │     │   EXPORT     │
│              │     │              │     └───────────────┘     │   GraphML    │
│              │     │              │                           │   GEXF, CSV  │
└──────────────┘     └──────────────┘                           └──────────────┘
```

### Stage 1 — Ingestion

Streams the HuggingFace dataset row by row, detects document boundaries, extracts person names using **spaCy NER** (primary) + regex/phonebook (secondary), and tracks per-name statistics: document count, co-occurring companions, sample contexts.

**Name extraction strategy:**
1. **spaCy NER (primary gate)** – `en_core_web_sm` tags PERSON entities (~10K chars/sec CPU). Blocks 90%+ of noise (dates, places, organizations).
2. **Phonebook (secondary validator)** – 20,000-name first-name database catches edge cases spaCy misses.
3. **Noise filter** – Regex patterns for known false positives (e.g., "In September", "Palm Beach").

```bash
python -m kg.ingest.from_hf_streaming --min-docs 5
```

Output: `real_mentions.jsonl` + `real_gold_aliases.jsonl`

### Stage 2 — Candidate generation (blocking)

For large corpora, comparing all pairs is O(n²) and infeasible. The pipeline uses **smart blocking**:

1. **Token-indexed lexical blocking** — index mentions by name tokens, only compare those sharing ≥1 token
2. **Abbreviation matching** — catches "J. Epstein" ↔ "Jeffrey Epstein"
3. **SequenceMatcher filtering** — ratio ≥ 0.72 for fuzzy matches
4. **Semantic kNN** — top-5 nearest neighbors by embedding cosine

### Stage 3 — Multi-signal scoring

Each candidate pair is scored on **9 independent behavioral signals**:

| Signal | What it measures | Alias intuition |
|--------|-----------------|-----------------|
| `name_similarity` | Cosine similarity of name embeddings | "Ehud Barak" ≈ "Ehud Barack" |
| `name_edit_distance` | SequenceMatcher ratio (char-level) | Catches OCR typos fallback can't |
| `last_name_edit_distance` | SequenceMatcher on surname token | Prevents first-name-only merges |
| `context_similarity` | Cosine similarity of surrounding text | Same person → similar contexts |
| `cooccurrence_score` | 1 − (shared docs / total docs) | Aliases rarely appear in same doc |
| `companion_overlap` | Jaccard of co-mentioned people | Same associates → same person |
| `location_overlap` | Jaccard of associated locations | Same places → same person |
| `role_match` | Structural role equality | Both "defendant" → likely same |
| `temporal_overlap` | Date proximity (decays over 365 days) | Same time period → same person |name
Signals are combined via learned weights into a single `weighted_score`.

**Fallback mode:** When SHA-256 embeddings are active (`--fallback-only`), the pipeline automatically collapses `name_similarity` and `context_similarity` weights to zero and redistributes their budget to non-embedding signals (edit distance, co-occurrence, companions). This prevents hash collisions from poisoning the score.

### Stage 4 — Weight optimisation

Given gold-standard alias labels (`match` / `no_match`), signal weights are optimised using **scipy Nelder-Mead** with margin-based hinge loss + L2 regularisation. Falls back to coordinate descent if scipy is unavailable.

### Stage 5 — Clustering, relationships & graph export

Pairs scoring above the auto-merge threshold are clustered via **Union-Find**. Each cluster becomes a `ResolvedEntity` with a canonical name (longest alias) and a list of all surface forms.

**Relationship extraction:** 40+ regex patterns identify typed relationships between co-mentioned people (`traveled_with`, `met_with`, `paid`, `accused`, `hired`, `arranged_for`, etc.). Edges are annotated with relationship types and evidence text.

**Graph export:** NetworkX-based export to:
- **GraphML** (Gephi, yEd, InfraNodus)
- **GEXF** (Gephi native format, with temporal `start`/`end` attributes)
- **CSV edge/node lists** (any tool, spreadsheet analysis)
- **Graphistry** (interactive GPU graph UI via Neo4j query)

Graph schema (v2):
- **Entity nodes** (`node_class=entity`) with aliases, `merge_confidence`, temporal range
- **Document nodes** (`node_class=document`) with `doc_id`, `doc_type`, mention/entity counts
- **Entity↔Entity edges** with `weight`, `relations`, and **full** `doc_ids` provenance (not sampled)
- **Entity↔Document edges** (`relation=mentioned_in`) to support A→Document→B investigative queries

## Quick start

```bash
# 1. Install dependencies
pip install sentence-transformers datasets scipy numpy spacy networkx lxml
python -m spacy download en_core_web_sm

# 2. Extract mentions from HuggingFace (streams ~2.1M rows, takes ~10 min)
python -m kg.ingest.from_hf_streaming --min-docs 5

# 3. Run the resolution pipeline
python -m kg.pipelines.resolve_aliases \
    --input kg/real_mentions.jsonl \
    --output kg/output_v9 \
    --gold kg/real_gold_aliases.jsonl \
    --fallback-only

# 4. View results
python kg/show_entities.py

# 5. Analyze the graph in Gephi / InfraNodus
# Load: kg/output_v9/graph/knowledge_graph.graphml
```

### CLI reference

```
python -m kg.pipelines.resolve_aliases [OPTIONS]
```

| Argument | Default | Description |
|---|---|---|
| `--input` | *(required)* | Path to mentions JSONL |
| `--output` | *(required)* | Output directory |
| `--model-name` | `all-MiniLM-L6-v2` | Sentence-transformers model name |
| `--auto-threshold` | `0.55` | Score ≥ this → auto merge |
| `--review-threshold` | `0.35` | Score ≥ this → human review queue |
| `--mode` | `behavioral` | `behavioral` (multi-signal) or `embedding` (cosine only) |
| `--gold` | `None` | Gold alias labels for weight optimisation + evaluation |
| `--weights` | `None` | Pre-learned weights JSON (skip re-optimisation) |
| `--fallback-only` | `False` | Use SHA-256 deterministic embeddings instead of transformer model |
| `--export-graph` | `True` | Export knowledge graph as GraphML/GEXF/CSV |
| `--no-export-graph` | — | Disable graph export |
| `--enrich-nationality` | `False` | Add nationality to person entities via Wikidata |
| `--nationality-cache` | `None` | Path to nationality cache JSON (default: kg/cache/nationality_cache.json) |

## Graphistry (Neo4j)

If you prefer Graphistry over Gephi/GraphML, use Neo4j as the query source and render directly:

```python
import graphistry
graphistry.register(api=3, username="...", password="...")

# Pull from Neo4j, render instantly
g = graphistry.cypher("MATCH (a:Person)-[r]-(b:Person) RETURN a,r,b LIMIT 500")
g.plot()
```

Project helper script (recommended for reproducibility):

```bash
python -m kg.plot_graphistry_neo4j \
  --graphistry-username YOUR_GRAPHISTRY_USER \
  --graphistry-password YOUR_GRAPHISTRY_PASS \
  --neo4j-uri neo4j+s://YOUR_NEO4J_HOST \
  --neo4j-user neo4j \
  --neo4j-password YOUR_NEO4J_PASS \
  --cypher "MATCH (a:Person)-[r]-(b:Person) RETURN a,r,b LIMIT 500"
```

Notes:
- Cypher query must return columns named exactly: `a`, `r`, `b`.
- Script converts Neo4j nodes/edges into Graphistry DataFrames and opens a share URL.
- For timeline-style exploration in Graphistry, include edge date properties in Neo4j and return them in `r`.

## Graphistry (no Neo4j, recommended)

You can render directly from this project's CSV exports (better visuals, zero DB setup):

```bash
python -m kg.plot_graphistry_csv \
  --graphistry-username YOUR_GRAPHISTRY_USER \
  --graphistry-password YOUR_GRAPHISTRY_PASS \
  --graph-dir kg/output_real_v11/graph
```

This reads:
- `edges.csv` (`Source`, `Target`, `Relation`, `DocIds`, ...)
- `nodes.csv` (`Id`, `Label`, `NodeClass`, ...)

And opens an interactive Graphistry URL where nodes are color-coded by `NodeClass`.

## Project structure

```
kg/
├── schemas.py                    # Dataclasses: Mention, CandidateScore, ReviewItem, ResolvedEntity
│
├── ingest/                       # Raw data → Mention JSONL
│   ├── phonebook.py              # Name validation (20K first names + surname DB)
│   ├── from_hf_streaming.py      # ★ Primary: stream from HuggingFace with spaCy NER
│   ├── from_hf_dataset.py        # Ingest from local CSV download (legacy)
│   ├── from_epstein_network.py   # Ingest from epstein-network repo (legacy)
│   └── data/
│       ├── first_names.txt       # ~20,000 first names
│       └── surnames.txt          # ~86,000 surnames
│
├── nlp/
│   ├── embed.py                  # EmbeddingService (sentence-transformers / SHA-256 fallback)
│   ├── ner.py                    # spaCy-based NER for person name extraction
│   └── relations.py              # Regex-based relationship extraction (40+ patterns)
│
├── enrich/
│   └── nationality.py            # Wikidata nationality enrichment + local cache
│
├── resolve/                      # Entity resolution engine
│   ├── scorer.py                 # Blocking, candidate generation, embedding-mode scoring
│   ├── signals.py                # 9-signal behavioral scorer + fallback weight collapsing
│   ├── cluster.py                # Union-Find → ResolvedEntity
│   └── feedback.py               # Gold label loading, weight optimisation, P/R/F1 evaluation
│
├── export/                       # Graph export
│   └── graph.py                  # NetworkX → GraphML/GEXF/CSV with document nodes + full provenance
│
├── pipelines/
│   └── resolve_aliases.py        # Main CLI pipeline
│
├── validate_cooccurrence.py      # Diagnostic: co-occurrence signal evaluation
├── real_mentions.jsonl            # Extracted mentions (2,926 at min_docs=5)
├── real_mentions_500.jsonl        # Top 500 subset for testing
├── real_gold_aliases.jsonl        # Gold-standard alias pairs
└── output_real_v8/                # Latest pipeline output
    ├── candidates.jsonl           # All scored pairs
    ├── auto_merges.jsonl          # Pairs above auto-merge threshold
    ├── review_queue.jsonl         # Pairs for human review
    ├── resolved_entities.jsonl    # Final merged entities
    ├── learned_weights.json       # Optimised signal weights
    ├── summary.json               # Run statistics
    └── graph/                     # Graph exports
        ├── knowledge_graph.graphml
        ├── knowledge_graph.gexf
        ├── edges.csv
        └── nodes.csv
```

## Data models

### Mention
```json
{
  "mention_id": "hf_b9c222cff7",
  "text": "Ehud Barak",
  "context": "Jeffrey Epstein and Ehud Barak were seen together...",
  "entity_type": "person",
  "source_doc_id": "doc_12345",
  "doc_type": "fbi_report",
  "structural_role": "subject",
  "companions": ["Jeffrey Epstein", "Ghislaine Maxwell"],
  "locations": ["New York", "Tel Aviv"],
  "date_ref": "2002-06-15"
}
```

### ResolvedEntity
```json
{
  "entity_id": "entity_000042",
  "entity_type": "person",
  "canonical_name": "Virginia Roberts Giuffre",
  "mention_ids": ["hf_abc123", "hf_def456", "hf_ghi789"],
  "aliases": ["Virginia Roberts", "Virginia Giuffre", "Virginia Roberts Giuffre"],
  "merge_confidence": 0.812345,
  "relationships": ["met_with", "associated_with"],
  "nationality": "Israeli",
  "first_seen_date": "2002-06-15",
  "last_seen_date": "2012-09-03",
  "source_doc_ids": ["doc_12345", "doc_55501", "doc_88902"]
}
```

### Graph edge attributes (Entity↔Entity)
```json
{
  "edge_class": "entity_entity",
  "relation": "co_occurrence",
  "relations": "co_occurrence; met_with",
  "weight": 12,
  "doc_count": 12,
  "doc_ids": "doc_1001; doc_1007; doc_1072; ...",
  "start": "2001-01-12",
  "end": "2013-11-20",
  "evidence": "..."
}
```

### GEXF temporal usage
`knowledge_graph.gexf` now includes `start` and `end` on nodes/edges (ISO dates when present), so Gephi timeline animation can be enabled directly from the export.

## Current results (v7, 501 mentions)

| Metric | Value |
|--------|-------|
| Mentions processed | 501 |
| Candidate pairs | 768 |
| Auto-merges | 59 |
| Resolved entities | 459 |
| Best F1 | **0.849** (at threshold 0.45) |
| Precision | 0.737 |
| Recall | 1.000 |

Notable merges:
- Jeffrey Epstein + Jeffrey Edward Epstein
- Virginia Roberts + Virginia Giuffre + Virginia Roberts Giuffre
- Brad Edwards + Bradley Edwards
- Jean Luc + Jean Luc Brunel
- Alexander Acosta + R. Alexander Acosta
- Marine Le Pen + Le Pen

## Known limitations

- **First-name merging with fallback embeddings** — SHA-256 fallback can't distinguish "Michael Cohen" from "Michael Jackson". Even with the new edit-distance signal and weight collapsing, the optimiser over-weights shared first names. Use a real transformer model (`--no-fallback-only`) for production.
- **Memory** — the full 2,926-mention corpus generates ~18K candidate pairs; batch embedding can OOM on machines with <8GB RAM. The 501-mention subset works reliably.
- **Noise entities** — some non-person strings leak through spaCy + phonebook (e.g., "In September", dates with capital letters). The `_NOISE_RE` pattern is continually expanded.
- **Co-occurrence signal** — needs validation against gold labels. Use `kg/validate_cooccurrence.py` to check if it's helping or hurting.

## Dependencies

| Package | Required | Purpose |
|---------|----------|---------|
| `spacy` + `en_core_web_sm` | Yes | Primary NER filter (fast, blocks noise) |
| `sentence-transformers` | Optional | Real embedding model (recommended) |
| `datasets` | For ingestion | HuggingFace streaming |
| `networkx` + `lxml` | For graph export | GraphML/GEXF generation |
| `scipy` | Optional | Nelder-Mead weight optimisation |
| `numpy` | Optional | Vectorized kNN in blocking |

## License

Research use only. The underlying Epstein documents are public records (DOJ/FBI declassifications, court filings).
