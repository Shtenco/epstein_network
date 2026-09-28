import json
from pathlib import Path
from epstein_network.synergy_contracts import CONTRACT_ID, provenance_graph_payload

def test_provenance_graph_does_not_infer_wrongdoing(tmp_path: Path):
    vendor=tmp_path/"vendor"; vendor.mkdir()
    source=vendor/"fixture"; source.mkdir()
    (source/"records.json").write_text(json.dumps([
        {"name":"Example Person","email":"person@example.invalid"},
        {"from":"a@example.invalid","to":"b@example.invalid"}
    ]),encoding="utf-8")
    p=provenance_graph_payload(snapshot_id="snap-1",vendor=vendor,out=tmp_path/"out")
    assert CONTRACT_ID=="synergy.science.provenance-graph/v1"
    assert p["records_scanned"]==2
    assert p["relationship_semantics_preserved"] is True
    assert p["wrongdoing_inference_authority"] is False
