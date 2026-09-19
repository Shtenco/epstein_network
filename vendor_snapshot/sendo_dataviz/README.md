# Epstein Files — Network Analysis

An interactive network visualization of the publicly released Epstein Files, mapping documented relationships between individuals and institutions using NER-based co-occurrence analysis.

**Live:** [data.kulakci.de](https://data.kulakci.de) · **Data story:** [data.kulakci.de/docs](https://data.kulakci.de/docs)

---

## What it does

- Downloads and samples the [Epstein Files dataset](https://huggingface.co/datasets/Nikity/Epstein-Files) from HuggingFace
- Runs spaCy NER (PERSON + ORG) over the PDF text corpus
- Builds a co-occurrence graph and computes betweenness centrality, clustering coefficients, and community detection via Louvain
- Renders an interactive force-directed network with [Cosmograph](https://cosmograph.app) (React + WebGPU)
- Publishes a Quarto data story documenting the full analysis pipeline

## Project structure

| Phase | Folder | Doc |
|---|---|---|
| Data Acquisition & Exploration | `eda/` | `docs/data_report.qmd` |
| Visual Encoding & Design | `viz_design/` | `docs/viz_design_report.qmd` |
| Evaluation | `evaluation/` | `docs/evaluation.qmd` |
| Deployment | — | `docs/deployment.qmd` |
| Frontend app | `frontend/` | — |

## Setup

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.template .env   # add HF_TOKEN
```

## Running the pipeline

```bash
uv run python eda/01_sample.py        # sample parquet shards from HuggingFace
uv run python eda/03_extract_entities.py  # NER + co-occurrence graph
uv run python eda/04_build_network.py     # network metrics + community detection
uv run python eda/05_export_frontend.py   # export JSON for the React app
```

## Frontend

```bash
cd frontend
npm install
npm run dev      # local dev server
npm run build    # production build → frontend/dist/
```

## Documentation

```bash
cd docs
uv run quarto render   # renders to docs/build/, updates docs/_freeze/
quarto preview         # live preview with hot reload
```

Commit `docs/_freeze/` after rendering so CI can build without Python.

## Deployment

Every push to `main` triggers `.github/workflows/publish.yml`, which builds the React app and renders the Quarto site, then deploys both to GitHub Pages.
