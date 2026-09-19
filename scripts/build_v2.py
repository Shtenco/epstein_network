from pathlib import Path
import json
from epstein_network.build import build
from epstein_network.entity_resolution import resolve

root=Path(__file__).resolve().parents[1]
stats=build(root/"vendor_snapshot",root/"data/processed")
er=resolve(root/"data/processed/nodes.csv",root/"data/processed/entity_map.csv",root/"data/processed/entity_review.csv")
(root/"data/processed/v2_stats.json").write_text(json.dumps({"graph":stats,"entity_resolution":er},indent=2),encoding="utf-8")
print(json.dumps({"graph":stats,"entity_resolution":er},indent=2))
