from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .build import build

CONTRACT_ID = "synergy.science.provenance-graph/v1"
AUTHORITY = "source_provenance_graph"


def provenance_graph_payload(*, snapshot_id: str, vendor: Path, out: Path) -> dict[str, Any]:
    if not snapshot_id.strip():
        raise ValueError("snapshot_id required")
    stats = build(vendor, out)
    evidence_path = out / "evidence.jsonl"
    edges_path = out / "edges.csv"
    nodes_path = out / "nodes.csv"
    return {
        "snapshot_id": snapshot_id,
        "nodes": int(stats["nodes"]),
        "edges": int(stats["edges"]),
        "records_scanned": int(stats["records_scanned"]),
        "nodes_sha256": sha256(nodes_path.read_bytes()).hexdigest(),
        "edges_sha256": sha256(edges_path.read_bytes()).hexdigest(),
        "evidence_sha256": sha256(evidence_path.read_bytes()).hexdigest(),
        "relationship_semantics_preserved": True,
        "wrongdoing_inference_authority": False,
        "identity_claim_authority": False,
    }
